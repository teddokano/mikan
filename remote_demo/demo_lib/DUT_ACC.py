import	machine
import	ure
import	ujson
import	micropython

from	nxp_periph	import	FXOS8700, FXLS8974
from	nxp_periph	import	ACCELEROMETER_base
from	demo_lib	import	DUT_base

class DUT_ACC( DUT_base.DUT_base ):
	APPLIED_TO		= ACCELEROMETER_base
	TABLE_LENGTH	= 10
	SAMPLE_LENGTH	= 60
	GRAPH_HIGH		= 2
	GRAPH_LOW		= -2

	DS_URL		= { "FXOS8700": "https://www.nxp.com/docs/en/data-sheet/FXOS8700CQ.pdf",
					"FXLS8974": "https://www.nxp.jp/docs/en/data-sheet/FXLS8974CF.pdf",
					}

	regex_update	= ure.compile( r".*update=(\d+)" )
	regex_settings	= ure.compile( r".*settings" )

	def __init__( self, dev, timer = 0, sampling_interval = 1.0 ):
		super().__init__( dev )
		
		self.read_ref	= self.__read
		self.data		= []
		self.rtc		= machine.RTC()	#	for timestamping on samples
		self.info		= [ "acc", "" ]
		self.symbol		= '🍎'

		if ( isinstance( self.dev, FXOS8700 ) ):
			self.split	= splits	= ( {	"id"	 	: "acc", 
											"unit"	 	: "g",
											"get_data"	: self.dev.xyz,
											"setting"	: graph_setting( 	[	{ "label": "x", "color": "rgba( 255,   0,   0, 1 )"},
																				{ "label": "y", "color": "rgba(   0, 255,   0, 1 )"},
																				{ "label": "z", "color": "rgba(   0,   0, 255, 1 )"},
																			], 
																			title	= '"g" now', 
																			xlabel	= 'time',
																			ylabel	= 'gravitational acceleration [g]',
																			minmax	= ( -2, 2 )
																			),
										}, 
										{ 
											"id"	 	: "mag", 
											"unit"	 	: "nT",
											"get_data"	: self.dev.mag,
											"setting"	: graph_setting( 	[	{ "label": "x", "color": "rgba( 255,   0,   0, 1 )"},
																				{ "label": "y", "color": "rgba(   0, 255,   0, 1 )"},
																				{ "label": "z", "color": "rgba(   0,   0, 255, 1 )"},
																			 ], 
																			 title	= '"mag" now', 
																			 xlabel	= 'time',
																			 ylabel	= 'geomagnetism [nT]',
																			 ),
										}, )

		elif ( isinstance( self.dev, FXLS8974 ) ):
			self.split	= splits	= ( {	"id"	 	: "acc", 
											"unit"	 	: "g",
											"get_data"	: self.dev.xyz,
											"setting"	: graph_setting( 	[	{ "label": "x", "color": "rgba( 255,   0,   0, 1 )"},
																				{ "label": "y", "color": "rgba(   0, 255,   0, 1 )"},
																				{ "label": "z", "color": "rgba(   0,   0, 255, 1 )"},
																			], 
																			title	= '"g" now', 
																			xlabel	= 'time',
																			ylabel	= 'gravitational acceleration [g]',
																			minmax	= ( -2, 2 )
																			),
										}, )
						
	def xyz_data( self ):
		d	= {}
		for splt in self.split:
			xyz	= splt[ "get_data" ]()
		
			for i, ds in enumerate( splt[ "setting" ].data[ "datasets" ] ):
				d[ splt[ "id" ] + ds[ "label" ] ]	= xyz[ i ]
		
		tm	= self.rtc.now()
		d[ "time" ]	= "%02d:%02d:%02d" % (tm[3], tm[4], tm[5])

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

			m	= self.regex_settings.match( req )
			if m:
				s	= []
				d	= {}
				for splt in self.split:
					d[ "id" ]		= splt[ "id" ]
					d[ "setting" ]	= splt[ "setting" ].__dict__
					s	+= [ ujson.dumps( d ) ]
				s	= ",".join( s )
				
				return "["+ s +"]"

	def sending_data( self, length ):
		return ujson.dumps( self.data[ -length: ] )

	def page_setup( self ):
		self.page_data[ "symbol"    ]	= self.symbol
		self.page_data[ "table_len" ]	= str( self.TABLE_LENGTH )
		self.page_data[ "tables"     ]	= self.get_tables()
		self.page_data[ "info_tab"  ]	= self.get_info_table()

		self.page_data[ "graph_high"]	= str( self.GRAPH_HIGH )
		self.page_data[ "graph_low" ]	= str( self.GRAPH_LOW  )
		self.page_data[ "max_n_data"]	= str( self.SAMPLE_LENGTH )

		self.page_data[ "charts" ]		= self.get_charts()

		return self.load_html()

	def get_charts( self ):
		s	= []
		for d in self.split:
			s	+= [ '<div><canvas id="{}"></canvas></div>'.format( d[ "id" ] ) ]

		return "\n".join( s )

	def get_tables( self ):
		s	= []
		for d in self.split:
			s	+= [ '<div id="reg_table" class="control_panel reg_table log_panel">' ]
			s	+= [ self.get_tab( d[ "id" ], d[ "unit" ], d[ "setting" ].data[ "datasets" ] ) ]
			s	+= [ '</div>' ]
		
		return "\n".join( s )
			
	def get_tab( self, id, unit, datasets ):
		s	= [ '<table class="table_TEMP"><tr><td class="td_TEMP">time</td><td class="td_TEMP">x [{0}]</td><td class="td_TEMP">y [{0}]</td><td class="td_TEMP">z [{0}]</td></tr>'.format( unit ) ]

		for i in range( self.TABLE_LENGTH ):
			s	+= [ '<tr>' ]
			s	+= [ '<td class="td_TEMP" text_align="center"><input class="input_text_TMP" type="text" id="{}timeField{}" value = "---"></td>'.format( id, i ) ]

			for ds in datasets:
				s	+= [ '<td class="td_TEMP"><input class="input_text_TMP" type="text" id="{}{}Field{}"></td>'.format( id, ds[ "label" ], i ) ]

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

class graph_setting:
	def __init__( self, datasets, type = "line", title = "title", xlabel = "", ylabel = "", minmax = () ):
		self.type		= type, 
		self.data		= { "labels": [], 
							"datasets": []
						  }
		self.options	= {
							"aspectRatio":3,
							"animation":False,
							"plugins": {
								"title": {
									"display":	True,
									"text": 	title
								}
							},
							"scales": {
								"y": {
									"ticks": {},
									"title": {
										"display": True,
										"text": ylabel
									}
								},
								"x": {
									"title": {
										"display": True,
										"text": xlabel
									}
								}
							},
						  }
			
		for i in datasets:
			set	= { "label"			: i[ "label" ],
					"borderColor"	: i[ "color" ],
					"lineTension"	: .5,
					"fill"			: False,
					"data"			: []
			}
			self.data[ "datasets" ]	+= [ set ]
			
		if len( minmax ) == 2:
			self.options[ "scales" ][ "y" ][ "suggestedMax" ]	= minmax[ 0 ] if minmax[ 1 ] < minmax[ 0 ] else minmax[ 1 ]
			self.options[ "scales" ][ "y" ][ "suggestedMin" ]	= minmax[ 0 ] if minmax[ 0 ] < minmax[ 1 ] else minmax[ 1 ]
