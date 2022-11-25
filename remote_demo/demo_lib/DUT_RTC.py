import	machine
import	ure
import	ujson

from	nxp_periph	import	PCF2131, PCF85063
from	nxp_periph	import	RTC_base
import	demo_lib.utils	as utils

class DUT_RTC():
	APPLIED_TO	= RTC_base
	
	WKDY	= ( "Monday", "Tuesday", "Wednesday",
				"Thursday", "Friday", "Saturday", "Sunday" )
	MNTH	= ( "None", "January", "February", "March",
				"April", "May", "June", "July", "August",
				"September", "October", "Nobemver", "Decemver" )

	DS_URL		= { "PCF2131_I2C": "https://www.nxp.com/docs/en/data-sheet/PCF2131DS.pdf",
					"PCF2131_SPI": "https://www.nxp.com/docs/en/data-sheet/PCF2131DS.pdf",
					"PCF85063": "https://www.nxp.com/docs/en/data-sheet/PCF85063A.pdf",
					}

	regex_reg	= ure.compile( r".*reg=(\d+)&val=(\d+)" )
	regex_alarm	= ure.compile( r".*alarm&weekday=(\d+)&day=(\d+)&hour=(\d+)&minute=(\d+)&second=(\d+)" )

	def __init__( self, dev ):
		self.interface	= dev.__if
		self.dev		= dev
		self.type		= self.dev.__class__.__name__
		self.info		= [ "Real Time Clock", "" ]
		self.symbol		= '\u23F0'
		
		if isinstance( self.interface, machine.I2C ):
			self.address	= dev.__adr
			self.dev_name	= self.type + "_on_I2C(0x%02X)" % (dev.__adr << 1)
		else:
			self.address	= dev.__cs
			self.dev_name	= self.type + "_on_SPI({})".format( dev.__cs )

	def parse( self, req ):
		if self.dev_name not in req:
			return None
	
		if "?" not in req:
			return self.page_setup()
		elif "set_current_time" in req:
			self.dev.datetime( machine.RTC().datetime() )
			return 'HTTP/1.0 200 OK\n\n'	# dummy
		elif "clear_alarm" in req:
			self.dev.clear_alarm()
			return 'HTTP/1.0 200 OK\n\n'	# dummy
		else:
			m	= self.regex_reg.match( req )
			if m:
				reg	= int( m.group( 1 ) )
				val	= int( m.group( 2 ) )

				self.dev.write_registers( reg, val )
				return 'HTTP/1.0 200 OK\n\n' + ujson.dumps( { "reg": reg, "val": val } )

			m	= self.regex_alarm.match( req )
			if m:
				alarm_time	= {
									"weekday"	: int( m.group( 1 ) ),
									"day"		: int( m.group( 2 ) ),
									"hours"		: int( m.group( 3 ) ),
									"minutes"	: int( m.group( 4 ) ),
									"seconds"	: int( m.group( 5 ) ),
							  }
				
				self.dev.clear_alarm()
				self.dev.alarm_int( None, **alarm_time )	#	No INT pin assertion to avoid other device (PCA9957-ARD)
				return 'HTTP/1.0 200 OK\n\n'	# dummy
			else:
				return self.sending_data()

	def sending_data( self ):
		if ( "PCF2131" in self.type ):
			tsl	= self.dev.timestamp()
			ts	= self.dev.timestamp2str( tsl )
		else:
			ts	= None
		
		alm_ofst	= self.dev.REG_NAME.index( "Second_alarm" )
		reg			= self.dev.dump()
		alarm_flg	= True if "alarm" in self.dev.check_events( self.dev.interrupt_clear() ) else False
		alarm		= reg[ alm_ofst : alm_ofst + 5 ]
		td			= self.dev.__get_datetime_reg()
		
		td[ "weekday" ]	= self.WKDY[ td[ "weekday" ] ]
		td[ "month"   ]	= self.MNTH[ td[ "month"   ] ]
		td[ "str"   ]	 = "%04d %s %02d (%s) %02d:%02d:%02d" % \
							(td[ "year" ], td[ "month" ], td[ "day" ], td[ "weekday" ], \
							td[ "hours" ], td[ "minutes" ], td[ "seconds" ] )
		
		return 'HTTP/1.0 200 OK\n\n' + ujson.dumps( { "datetime": td, "reg": reg, "ts": ts, "alarm_flg": alarm_flg, "alarm": alarm } )

	def page_setup( self ):
		html	= "HTTP/1.0 200 OK\n\n{% html %}"
		
		page_data	= {}
		page_data[ "dev_name"  ]	= self.dev_name
		page_data[ "dev_type"  ]	= self.type
		page_data[ "dev_link"  ]	= '<a href="{}" target="_blank" rel="noopener noreferrer">{}</a>'.format( self.DS_URL[ self.type ], self.type )
		page_data[ "symbol"    ]	= self.symbol
		page_data[ "dev_info"  ]	= self.dev.info()
		page_data[ "signature" ]	= utils.page_signature()
		page_data[ "reg_table" ]	= self.get_reg_table( 4 )
		page_data[ "timestamp" ]	= '<div id="timestamp" class="timestamp">timestamps<br/></div>' if "PCF2131" in self.type else ''
		page_data[ "sound"     ]	= utils.get_sound( "demo_lib/sound.data" )

		if len( page_data[ "sound" ] ) is 0:
			print( "####### DUT_RTC: No sound data loaded" )
		else:
			print( "####### DUT_RTC: Sound data loaded" )

		files	= [ [ 	"html", 	"demo_lib/" + self.__class__.__name__	],
					[	"css", 		"demo_lib/general"						],
					[	"js",		"demo_lib/general",
									"demo_lib/" + self.__class__.__name__ 	]
				  ]

		html	= utils.file_loading( html, files )
		
		for key, value in page_data.items():
			html = html.replace('{% ' + key + ' %}', value )
		
		return html

	def get_reg_table( self, cols ):
		total	= len( self.dev.REG_NAME )
		rows	= (total + cols - 1) // cols

		s	 	= [ '<table class="table_RTC">' ]

		for y in range( rows ):
			s	 	+= [ '<tr class="reg_table_row">' ]
			for i in range( y, total, rows ):
				s	+= [ '<td class="td_RTC reg_table_name">{}</td><td class="td_RTC reg_table_val">0x{:02X}</td>'.format( self.dev.REG_NAME[ i ], i ) ]
				s	+= [ '<td class="td_RTC reg_table_val"><input type="text" onchange="updateRegField( this, {} )" id="regField{}" minlength=2 size=2 value="--" class="regfield"></td>'.format( i, i ) ]

			s	+= [ '</tr>' ]

		s	+= [ '</table>' ]
		return "\n".join( s )
