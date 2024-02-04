import	machine
import	ure
import	ujson

from	nxp_periph	import	PCF2131, PCF85063A
from	nxp_periph	import	RTC_base
from	demo_lib	import	DUT_base

class DUT_RTC( DUT_base.DUT_base ):
	APPLIED_TO	= RTC_base
	
	WKDY	= ( "Monday", "Tuesday", "Wednesday",
				"Thursday", "Friday", "Saturday", "Sunday" )
	MNTH	= ( "None", "January", "February", "March",
				"April", "May", "June", "July", "August",
				"September", "October", "November", "December" )

	DS_URL		= { "PCF2131_I2C": "https://www.nxp.com/docs/en/data-sheet/PCF2131DS.pdf",
					"PCF2131_SPI": "https://www.nxp.com/docs/en/data-sheet/PCF2131DS.pdf",
					"PCF85063A": "https://www.nxp.com/docs/en/data-sheet/PCF85063A.pdf",
					}

	regex_reg	= ure.compile( r".*reg=(\d+)&val=(\d+)" )
	regex_alarm	= ure.compile( r".*alarm&weekday=(\d+)&day=(\d+)&hour=(\d+)&minute=(\d+)&second=(\d+)" )
	regex_pc_t	= ure.compile( r".*set_pc_time=(\d+)-(\d+)-(\d+)T(\d+):(\d+):(\d+).(\d+)Z&weekday=(\S+)\?" )

	def __init__( self, dev ):
		super().__init__( dev )
		self.info		= [ "Real Time Clock", "" ]
		self.symbol		= '\u23F0'
		

	def parse( self, req ):
		if self.dev_name not in req:
			return None
	
		if "?" not in req:
			return self.page_setup()
		elif "set_current_time" in req:
			self.dev.datetime( machine.RTC().datetime() )
			return ""	# dummy
		elif "clear_alarm" in req:
			self.dev.clear_alarm()
			return ""	# dummy
		else:
			m	= self.regex_reg.match( req )
			if m:
				reg	= int( m.group( 1 ) )
				val	= int( m.group( 2 ) )

				self.dev.write_registers( reg, val )
				return ujson.dumps( { "reg": reg, "val": val } )

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
				return ""	# dummy

			m	= self.regex_pc_t.match( req )
			if m:
				t	= ( int( m.group( 1 ) ), 
						int( m.group( 2 ) ), 
						int( m.group( 3 ) ), 
						self.WKDY.index( m.group( 8 ).decode() ), 
						int( m.group( 4 ) ), 
						int( m.group( 5 ) ), 
						int( m.group( 6 ) ) 
						)
				self.dev.datetime( t )
				return ""	# dummy
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
		
		return ujson.dumps( { "datetime": td, "reg": reg, "ts": ts, "alarm_flg": alarm_flg, "alarm": alarm } )

	def page_setup( self ):
		self.page_data[ "symbol"    ]	= self.symbol
		self.page_data[ "reg_table" ]	= self.get_reg_table( 4 )
		self.page_data[ "timestamp" ]	= '<div id="timestamp" class="timestamp">timestamps<br/></div>' if "PCF2131" in self.type else ''
		self.page_data[ "sound"     ]	= self.load_file( "demo_lib/sound.data" )

		if len( self.page_data[ "sound" ] ) is 0:
			print( "####### DUT_RTC: No sound data loaded" )
		else:
			print( "####### DUT_RTC: Sound data loaded" )

		return self.load_html()

	def get_reg_table( self, cols ):
		total	= len( self.dev.REG_NAME )
		rows	= (total + cols - 1) // cols

		s	 	= [ '<table class="table_RTC">' ]

		for y in range( rows ):
			s	 	+= [ '<tr class="reg_table_row">' ]
			for i in range( y, total, rows ):
				s	+= [ '<td class="td_RTC reg_table_name">{}</td><td class="td_RTC reg_table_val">0x{:02X}</td>'.format( self.dev.REG_NAME[ i ], i ) ]
				s	+= [ '<td class="td_RTC reg_table_val"><input type="text" onchange="updateRegField( {} )" id="regField{}" minlength=2 size=2 value="--" class="regfield"></td>'.format( i, i ) ]

			s	+= [ '</tr>' ]

		s	+= [ '</table>' ]
		return "\n".join( s )
