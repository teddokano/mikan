import	machine
import	ure
import	ujson
import	micropython

from	nxp_periph	import	FXOS8700
from	demo_lib	import	DUT_base

class DUT_ACC( DUT_base.DUT_base ):
	APPLIED_TO		= FXOS8700
	TABLE_LENGTH	= 10
	SAMPLE_LENGTH	= 60
	GRAPH_HIGH		= 2
	GRAPH_LOW		= -2

	DS_URL		= { "FXOS8700": "https://www.nxp.com/docs/en/data-sheet/FXOS8700CQ.pdf",
					}

	regex_update	= ure.compile( r".*update=(\d+)" )

	def __init__( self, dev, timer = 0, sampling_interval = 1.0 ):
		super().__init__( dev )
		
		self.read_ref	= self.__read
		self.data		= []
		self.rtc		= machine.RTC()	#	for timestamping on samples
		self.info		= [ "acc", "" ]
		self.symbol		= '🍎'

	def xyz_data( self ):
		d	= {}
		xyz	= self.dev.xyz()
#		xyz	= self.dev.mag()
		d[ "x" ] = xyz[ 0 ]
		d[ "y" ] = xyz[ 1 ] 
		d[ "z" ] = xyz[ 2 ]
		tm	= self.rtc.now()
		d[ "time"   ]	= "%02d:%02d:%02d" % (tm[3], tm[4], tm[5])

		return d

	def __read( self, _ ):
		self.data	+= [ self.xyz_data() ]

		over	= len( self.data ) - self.SAMPLE_LENGTH
		if  0 < over:
			self.data	= self.data[ over : ]

		# print( "sampled: {}".format( self.data[ -1 ] ) )

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
				self.__read( 0 )	# argument is dummy
				return self.sending_data( int( m.group( 1 ) ) )

	def sending_data( self, length ):
		return ujson.dumps( self.data[ -length: ] )

	def page_setup( self ):
		self.page_data[ "symbol"    ]	= self.symbol
		self.page_data[ "table_len" ]	= str( self.TABLE_LENGTH )
		self.page_data[ "table"     ]	= self.get_table()
		self.page_data[ "info_tab"  ]	= self.get_info_table()

		self.page_data[ "graph_high"]	= str( self.GRAPH_HIGH )
		self.page_data[ "graph_low" ]	= str( self.GRAPH_LOW  )
		self.page_data[ "max_n_data"]	= str( self.SAMPLE_LENGTH )

		return self.load_html()

	def get_table( self ):
		s	= [ '<table class="table_TEMP"><tr><td class="td_TEMP">time</td><td class="td_TEMP">x [g]</td><td class="td_TEMP">y [g]</td><td class="td_TEMP">z [g]</td></tr>' ]

		for i in range( self.TABLE_LENGTH ):
			s	+= [ '<tr>' ]
			s	+= [ '<td class="td_TEMP" text_align="center"><input class="input_text_TMP" type="text" id="timeField{}" value = "---"></td>'.format( i ) ]
			s	+= [ '<td class="td_TEMP"><input class="input_text_TMP" type="text" id="xField{}"></td>'.format( i ) ]
			s	+= [ '<td class="td_TEMP"><input class="input_text_TMP" type="text" id="yField{}"></td>'.format( i ) ]
			s	+= [ '<td class="td_TEMP"><input class="input_text_TMP" type="text" id="zField{}"></td>'.format( i ) ]
			s	+= [ '</tr>' ]

		s	+= [ '</table>' ]

		return "\n".join( s )

	def get_info_table( self ):
		lb	= [ "start time", "last time", "sample count" ]
		s	= [ '<table class="table_TEMP"><tr>' ]

		for i, l in zip( range( len( lb ) ), lb ):
			s	+= [ '<tr><td class="td_TEMP" text_align="center">{}</td><td class="td_TEMP"><input class="input_text_TMP" type="text" id="infoFieldValue{}"></td></tr>'.format( l, i ) ]

		s	+= [ '</table>' ]

		return "\n".join( s )
