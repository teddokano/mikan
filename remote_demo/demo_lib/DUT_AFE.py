import	machine
import	ure
import	ujson
import	micropython

from	nxp_periph	import	NAFE13388
#from	nxp_periph	import	P3T1755
from	nxp_periph	import	LM75B
from	nxp_periph	import	AFE_base
from	demo_lib	import	DUT_base

import	machine

DEFAULT_SETTING_FILE	= "demo_lib/local_setting/AFE_default_setting.json"
UPDATED_SETTING_FILE	= "demo_lib/local_setting/AFE_updated_setting.json"

class DUT_AFE( DUT_base.DUT_base ):
	APPLIED_TO		= AFE_base
	TABLE_LENGTH	= 10
	SAMPLE_LENGTH	= 60
	GRAPH_HIGH		= 2
	GRAPH_LOW		= -2

	DS_URL		= { "NAFE13388": "https://www.nxp.com/docs/en/data-sheet/NAFE11388DS.pdf",
					}

	regex_update			= ure.compile( r".*update=(\d+)" )
	regex_settings			= ure.compile( r".*settings" )
	regex_cal_weigt_scale	= ure.compile( r".*cal_weight_scale=(.+)\?" )
	regex_cal_temp			= ure.compile( r".*cal_temp=(.+)\?" )

	def __init__( self, dev, timer = 0, sampling_interval = 1.0 ):
		super().__init__( dev )
		
		
		self.setting	= { "weight": {}, "temperature": {}, "remark": "AFE demo updated setting file" }

		self.setting[ "weight"      ][ "ofst"  ]	= -38
		self.setting[ "weight"      ][ "coeff" ]	= 1044 / (354 - self.setting[ "weight" ][ "ofst" ])
		# self.setting[ "weight"      ][ "ofst"  ]	= -24
		# self.setting[ "weight"      ][ "coeff" ]	= 2
		self.setting[ "temperature" ][ "ofst"  ]	= -70
		self.setting[ "temperature" ][ "coeff" ]	= 1 / 40
		self.setting[ "temperature" ][ "base"  ]	= 25

		if not self.load_setting_file( UPDATED_SETTING_FILE ):
			self.load_setting_file( DEFAULT_SETTING_FILE )
		
		self.save_setting_file( UPDATED_SETTING_FILE )
		
		print( self.setting )
		
		self.read_ref	= self.__read
		self.data		= []
		self.rtc		= machine.RTC()	#	for timestamping on samples
		self.info		= [ "AFE", "" ]
		self.symbol		= '🌊'

		self.set_external_sensor()

		if ( isinstance( self.dev, NAFE13388 ) ):
			self.split	= splits	= ( {	"id"	 	: "acc", 
											"unit"	 	: "g",
											"get_data"	: self.temperature,
											"setting"	: graph_setting( 	[	{ "label": "temperature", "color": "rgba( 0, 128,   0, 1 )"},
																			], 
																			title	= 'temperature', 
																			xlabel	= 'time',
																			ylabel	= 'temperature [℃]',
																			minmax	= ( self.setting[ "scales" ][ 0 ][ "min" ], self.setting[ "scales" ][ 0 ][ "max" ] )
																			),
										}, 
										{ 
											"id"	 	: "mag", 
											"unit"	 	: "nT",
											"get_data"	: self.weight,
											"setting"	: graph_setting( 	[	{ "label": "weight", "color": "rgba( 0,   0, 255, 1 )"},
																			 ], 
																			 title	= 'weight', 
																			 xlabel	= 'time',
																			 ylabel	= 'weight [g]',
																			 minmax	= ( self.setting[ "scales" ][ 1 ][ "min" ], self.setting[ "scales" ][ 1 ][ "max" ] )
																			 ),
										}, )
	
		self.dev.periodic_measurement_start()

	def set_external_sensor( self ):
#		self.temp_sense	= P3T1755( machine.I2C( 0, 400_000 ), self.setting[ "temperature" ][ "target" ] >> 1 )
		self.temp_sense	= LM75B( machine.I2C( 0, 400_000 ), self.setting[ "temperature" ][ "target" ] >> 1 )
		
		rtn	= self.temp_sense.ping()
		print( f"* self.temp_sense.live = {self.temp_sense.live} (address = 0x{self.setting[ 'temperature' ][ 'target' ]:02X})" )
		print( f"* self.get_temp() = {self.get_temp()}" )

		return rtn

	def temperature( self ):
		t	= self.ch[ 0 ]
		
		if self.setting[ "temperature" ][ "select" ] == 0:
			base	= self.setting[ "temperature" ][ "base" ]
		elif self.setting[ "temperature" ][ "select" ] == 1:
			if self.setting[ "temperature" ][ "measured" ] is None:
				base	= self.setting[ "temperature" ][ "base" ]
			else:
				base	= self.setting[ "temperature" ][ "measured" ]
		else:
			base	= self.die_temp()
			
		return (t - self.setting[ "temperature" ][ "ofst" ]) * self.setting[ "temperature" ][ "coeff" ] + base
		
	def weight( self ):
		w	= self.ch[ 1 ]
		return (w - self.setting[ "weight" ][ "ofst" ]) * self.setting[ "weight" ][ "coeff" ]

	def weight_zero( self ):
		w	= self.ch[ 1 ]
		self.setting[ "weight" ][ "ofst" ]	= w

	def weight_cal( self, ref ):
		w	= self.ch[ 1 ]
		self.setting[ "weight" ][ "coeff" ]	= ref / (w - self.setting[ "weight" ][ "ofst" ])


	def get_temp( self ):
		if self.temp_sense.live:
			return self.temp_sense.temp
		else:
			return None

	def save_setting_file( self, path ):
		with open( path, mode = "w" ) as f:
			ujson.dump( self.setting, f )

	def load_setting_file( self, path ):
		try:
			with open( path ) as f:
				self.setting	= ujson.loads( f.read() )
				print( f'setting file loaded: "{path}"' )
		except ValueError:
			print( f'setting file load fail: "{path}". Syntax error in JSON' )
			return False
		
		except OSError:
			print( f'setting file load fail: "{path}". NO FILE FOUND' )
			return False
		
		return True


	def xyz_data( self ):
		d	= {}
		for splt in self.split:
			xyz	= splt[ "get_data" ]()
			
			for i, ds in enumerate( splt[ "setting" ].data[ "datasets" ] ):
				d[ splt[ "id" ] + ds[ "label" ] ]	= xyz
		
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
				if 1 == self.setting[ "temperature" ][ "select" ]:
					self.setting[ "temperature" ][ "measured" ]	= self.get_temp()
			
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
			
			m	= self.regex_cal_weigt_scale.match( req )
			if m:
				obj	= ujson.loads( bytearray( m.group( 1 ).decode().replace( '%22', '"' ), "utf-8" ) )
				print( f"cal value = {obj[ 'cal' ]}" )
				self.weight_cal( obj[ 'cal' ] )
				
				return
			
			m	= self.regex_cal_temp.match( req )
			if m:
				obj	= ujson.loads( bytearray( m.group( 1 ).decode().replace( '%22', '"' ), "utf-8" ) )
				
				self.setting[ "temperature" ][ "ofst"   ]	= obj[ "ofst"   ]
				self.setting[ "temperature" ][ "coeff"  ]	= obj[ "coeff"  ]
				self.setting[ "temperature" ][ "base"   ]	= obj[ "base"   ]
				self.setting[ "temperature" ][ "target" ]	= obj[ "target" ]
				self.setting[ "temperature" ][ "select" ]	= obj[ "select" ]
				
				self.setting[ "scales" ][ 0 ][ "max"  ]	= obj[ "scales" ][ 0 ][ "max"  ]
				self.setting[ "scales" ][ 0 ][ "min"  ]	= obj[ "scales" ][ 0 ][ "min"  ]
				self.setting[ "scales" ][ 1 ][ "max"  ]	= obj[ "scales" ][ 1 ][ "max"  ]
				self.setting[ "scales" ][ 1 ][ "min"  ]	= obj[ "scales" ][ 1 ][ "min"  ]
				
				self.save_setting_file( UPDATED_SETTING_FILE )

				self.set_external_sensor()
				
				print( "===== settings saved =====" )
				
				return
				
			if "weight_zero" in req:
				print( "weight_zero" )
				self.weight_zero()
				
				return
				
			if "start_setting" in req:
				print( "start_setting" )
				print( self.setting )
								
				return ujson.dumps( self.setting )

			if "load_default_setting" in req:
				print( "load_default_setting" )
				self.load_setting_file( DEFAULT_SETTING_FILE )
				
				return ujson.dumps( self.setting )

			if "get_temp_message" in req:
				die_temp	= self.dev.die_temp()
				
				if temp_read := self.get_temp():
					rtn	= f"ext_sensor read: {temp_read}℃\ndie temp = {die_temp}℃"
				else:
					rtn	= "ext_sensor is not responding\ndie temp = {die_temp}℃"
					
				return rtn
				


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
			s	+= [ '<div id="graph_{0}"><canvas id="{0}"></canvas></div>'.format( d[ "id" ] ) ]

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

