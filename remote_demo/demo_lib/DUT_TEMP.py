import	machine
import	ure
import	ujson

from	nxp_periph	import	PCT2075, LM75B
from	nxp_periph	import	temp_sensor_base
from	demo_lib	import	DUT_base

class DUT_TEMP( DUT_base.DUT_base):
	APPLIED_TO		= temp_sensor_base
	TABLE_LENGTH	= 10
	SAMPLE_LENGTH	= 60
	GRAPH_HIGH		= 30
	GRAPH_LOW		= 20

	DS_URL		= { "PCT2075": "https://www.nxp.com/docs/en/data-sheet/PCT2075.pdf",
					"LM75B": "https://www.nxp.com/docs/en/data-sheet/LM75B.pdf",
					}

	regex_thresh	= ure.compile( r".*tos=(\d+\.\d+)&thyst=(\d+\.\d+)" )
	regex_heater	= ure.compile( r".*heater=(\d+)" )
	regex_mode		= ure.compile( r".*os_polarity=(\d+)&os_mode=(\d+)" )
	regex_update	= ure.compile( r".*update=(\d+)" )

	def __init__( self, dev, timer = 0, sampling_interbal = 1.0 ):
		super().__init__( dev )
		self.data		= []
		self.rtc		= machine.RTC()	#	for timestamping on samples
		self.info		= [ "temp sensor", "" ]
		self.symbol		= '🌡️'

		if self.dev.ping():
			tp	= self.dev.temp
		else:
			tp	= 25	#	default value when device is not responding

		self.GRAPH_HIGH		= int( tp + 6 )
		self.GRAPH_LOW		= self.GRAPH_HIGH - 10

		self.tos		= int( (tp + 2) * 2 ) / 2
		self.thyst		= int( (tp + 1) * 2 ) / 2

		self.dev.temp_setting( [ self.tos, self.thyst ] )

		self.int_pin	= machine.Pin( "D2", machine.Pin.IN  )
		self.dev.heater	= 0

		if self.dev.live:
			tim0	= machine.Timer( timer )
			tim0.init( period = int( sampling_interbal * 1000.0 ), callback = self.tim_cb )

	def tmp_data( self ):
		d	= {}
		d[ "temp" ] = self.dev.temp
		tm	= self.rtc.now()

		d[ "time"   ]	= "%02d:%02d:%02d" % (tm[3], tm[4], tm[5])
		d[ "tos"    ]	= self.tos
		d[ "thyst"  ]	= self.thyst
		d[ "os"     ]	= self.GRAPH_HIGH if self.int_pin.value() else self.GRAPH_LOW
		d[ "heater" ]	= self.GRAPH_HIGH if self.dev.heater      else self.GRAPH_LOW
		
		return d

	def tim_cb( self, tim_obj ):
		self.data	+= [ self.tmp_data() ]

		over	= len( self.data ) - self.SAMPLE_LENGTH
		if  0 < over:
			self.data	= self.data[ over : ]

		#print( "sampled: {} @ {}".format( tp, tm ) )

	def parse( self, req ):
		if self.dev_name not in req:
			return None

		if "?" not in req:
			return	self.page_setup()
		else:
			#print( req )
			html	= ""	# dummy

			m	= self.regex_update.match( req )
			if m:
				return self.sending_data( int( m.group( 1 ) ) )

			m	= self.regex_thresh.match( req )
			if m:
				self.tos	= float( m.group( 1 ) )
				self.thyst	= float( m.group( 2 ) )
				self.dev.temp_setting( [ self.tos, self.thyst ] )
				print( "********** THRESHOLDS {} {} **********".format( self.tos, self.thyst ) )
				return html

			m	= self.regex_heater.match( req )
			if m:
				val	= int( m.group( 1 ) )
				self.dev.heater	= val
				print( "********** {} HEATER {} **********".format( self.type, "ON" if val else "OFF" ) )
				return html

			m	= self.regex_mode.match( req )
			if m:
				pol	= int( m.group( 1 ) )
				mod	= int( m.group( 2 ) )
				self.dev.bit_operation( "Conf", 0x06, (pol << 2) | (mod << 1) )
				print( "********** CONFIGURATION {} {} **********".format( "Active_HIGH" if pol else "Active_Low", "Interrupt" if mod else "Comparator" ) )
				return html

	def sending_data( self, length ):
		return ujson.dumps( self.data[ -length: ] )

	def page_setup( self ):
		self.page_data[ "symbol"    ]	= self.symbol
		self.page_data[ "table_len" ]	= str( self.TABLE_LENGTH )
		self.page_data[ "table"     ]	= self.get_table()
		self.page_data[ "info_tab"  ]	= self.get_info_table()

		self.page_data[ "graph_high"]	= str( self.GRAPH_HIGH )
		self.page_data[ "graph_low" ]	= str( self.GRAPH_LOW  )
		self.page_data[ "tos_init"  ]	= str( self.tos   )
		self.page_data[ "thyst_init"]	= str( self.thyst )
		self.page_data[ "max_n_data"]	= str( self.SAMPLE_LENGTH )

		return self.load_html()

	def get_table( self ):
		s	= [ '<table class="table_TEMP"><tr><td class="td_TEMP">time</td><td class="td_TEMP">temp [˚C]</td></tr>' ]

		for i in range( self.TABLE_LENGTH ):
			s	+= [ '<tr><td class="td_TEMP" text_align="center"><input class="input_text_TMP" type="text" id="timeField{}" value = "---"></td><td class="td_TEMP"><input class="input_text_TMP" type="text" id="tempField{}"></td></tr>'.format( i, i ) ]

		s	+= [ '</table>' ]

		return "\n".join( s )

	def get_info_table( self ):
		lb	= [ "start time", "last time", "sample count" ]
		s	= [ '<table class="table_TEMP"><tr>' ]

		for i, l in zip( range( len( lb ) ), lb ):
			s	+= [ '<tr><td class="td_TEMP" text_align="center">{}</td><td class="td_TEMP"><input class="input_text_TMP" type="text" id="infoFieldValue{}"></td></tr>'.format( l, i ) ]

		s	+= [ '</table>' ]

		return "\n".join( s )
