#	MicroPython HTTP server sample code based on "http_server_simplistic.py".
#	https://github.com/micropython/micropython/blob/master/examples/network/http_server_simplistic.py
#
#
#	Based on simple HTTP server code, Trying LED ON/OFF via web
#	https://gist.github.com/teddokano/45b99cd906e63a23105ab427ae70d1dc
#	https://forum.micropython.org/viewtopic.php?t=1940#p10926
#
#	Tedd OKANO / Released under the MIT license
#	22-Oct-2022
#	version	0.1

import	machine
import	os
import	ure
import	ujson

from	nxp_periph	import	PCA9956B, PCA9955B, PCA9632, PCA9957, LED
from	nxp_periph	import	LED_controller_base
import	demo_lib.utils	as utils


class DUT_LEDC():
	APPLIED_TO	= LED_controller_base
	IREF_INIT	= 0x10
	regex_pwm	= ure.compile( r".*value=(\d+)&idx=(\d+)" )
	regex_reg	= ure.compile( r".*reg=(\d+)&val=(\d+)" )
	
	DS_URL		= { "PCA9956B": "https://www.nxp.com/docs/en/data-sheet/PCA9956B.pdf",
					"PCA9955B": "https://www.nxp.com/docs/en/data-sheet/PCA9955B.pdf",
					"PCA9632": "https://www.nxp.com/docs/en/data-sheet/PCA9632.pdf",
					"PCA9957": "https://www.nxp.com/docs/en/data-sheet/PCA9957DS.pdf"
					}

	def __init__( self, dev ):
		self.interface	= dev.__if
		self.dev		= dev
		self.led		= [ LED( self.dev, i ) for i in range( self.dev.CHANNELS ) ]
		self.type		= self.dev.__class__.__name__
		self.info		= [ "LED controller", "{}ch".format( self.dev.CHANNELS ) ]

		if isinstance( self.interface, machine.I2C ):
			self.address	= dev.__adr
			self.dev_name	= self.type + "_on_I2C(0x%02X)" % (dev.__adr << 1)
		else:
			self.address	= dev.__cs
			self.dev_name	= self.type + "_on_SPI({})".format( dev.__cs )

	def parse( self, req ):
		#print( "!!!! %s: <--- request ---- \"%s\"" % ( self.dev_name, req.decode() ) )
		if self.dev_name not in req:
			return None
	
		if "?" not in req:
			if hasattr( self.dev, "__iref_base" ):
				self.IREF_ID_OFFSET	= 100
				self.dev.write_registers( "IREFALL", self.IREF_INIT )
			else:
				self.IREF_ID_OFFSET	= 0

#			for i in range( self.dev.CHANNELS ):
#				self.led[ i ].v	= 0.0

			html	= self.page_setup()

		elif "allreg" in req:
			html	= 'HTTP/1.0 200 OK\n\n' + ujson.dumps( { "reg": self.dev.dump() } )
		else:
			html	= 'HTTP/1.0 200 OK\n\n'	# dummy

			m	= self.regex_pwm.match( req )
			if m:
				#print( m.groups() )
				pwm	= int( m.group( 1 ) )
				ch	= int( m.group( 2 ) )
				
				if (self.IREF_ID_OFFSET is 0) or (ch < (self.IREF_ID_OFFSET - 1)):
					self.led[ ch ].v	= pwm / 255
				elif ch is (self.IREF_ID_OFFSET - 1):
					self.dev.write_registers( "PWMALL", pwm )
				elif ch < (self.IREF_ID_OFFSET * 2 - 1):
					self.led[ ch - self.IREF_ID_OFFSET ].i	= pwm / 255
				elif ch is (self.IREF_ID_OFFSET * 2 - 1):
					self.dev.write_registers( "IREFALL", pwm )
				else:
					pass

				html	= 'HTTP/1.0 200 OK\n\n' + ujson.dumps( { "val": pwm, "idx": ch } )

			m	= self.regex_reg.match( req )
			if m:
				#print( m.groups() )
				reg	= int( m.group( 1 ) )
				val	= int( m.group( 2 ) )

				self.dev.write_registers( reg, val )

				html	= 'HTTP/1.0 200 OK\n\n' + ujson.dumps( { "reg": reg, "val": val } )

		return html

	def page_setup( self ):
		#HTML to send to browsers
		html = """\
		HTTP/1.0 200 OK

		<!DOCTYPE html>
		<html>
			<head>
				<meta charset="utf-8" />
				<title>{% dev_name %} server</title>
				<style>
					{% css %}
				</style>
			</head>
			<body>
				<script>
					{% js %}
				</script>

				<div class="header">
					<p>{% dev_link %} server</p>
					<p class="info">{% dev_info %}</p>
				</div>
				
				<div class="control_panel slider_panel">
					PWM registers
					{% sliders_PWM %}
				</div>
				
				<div class="control_panel slider_panel">
					IREF registers
					{% sliders_IREF %}
				</div>

				<div id="reg_table" class="control_panel reg_table">
					register table<br/>
					{% reg_table %}
					<div class="button_and_note">
					<input type="button" onclick="allRegLoad();" value="reload" class="all_reg_load">
					{% allreg_note %}
					</div>
				</div>
				
				<div class="foot_note">
					<b>HTTP server on<br/>
					{% mcu %}</b><br/>
					0100111101101011011000010110111001101111
				</div>
		</body>
		</html>
		"""
		
		info	= self.dev.info()

		if "PCA9956B" in info:
			col_pat	= sum( tuple( ("R", "G", "B") for i in range( 8 ) ), () )
			all_reg = True
		elif "PCA9955B" in info:
			col_pat	= sum( tuple( ("K", "R", "G", "B") for i in range( 4 ) ), () )
			all_reg = True
		elif "PCA9957" in info:
			col_pat	= sum( tuple( ("R", "G", "B") for i in range( 4 ) ), () )
			col_pat	+= tuple( "K" for i in range( 12 ) )
			all_reg = True
		elif "PCA9632" in info:
			col_pat	= ("R", "G", "B", "K")
			all_reg = False
		else:
			separator	= 4
			all_reg = False

		iref		= hasattr( self.dev, "__iref_base" )
		
		count		= self.dev.CHANNELS
		pwm0_idx	= self.dev.REG_NAME.index( "PWM0"  )
		iref0_idx	= self.dev.REG_NAME.index( "IREF0" ) if iref else 0
		pwmall_idx	= self.dev.REG_NAME.index( "PWMALL"  ) if all_reg else 0
		irefall_idx	= self.dev.REG_NAME.index( "IREFALL" ) if all_reg else 0
		
		if all_reg:
			if irefall_idx:
				allreg_note	= "PWMAALL and OREFALL are write-only register. ignore loaded value"
			else:
				allreg_note	= "PWMAALL is a write-only register. ignore loaded value"
		else:
				allreg_note	= ""

		page_data	= {}
		page_data[ "dev_name"    ]	= self.dev_name
		page_data[ "dev_type"    ]	= self.type
		page_data[ "dev_link"    ]	= '<a href="{}" target="_blank" rel="noopener noreferrer">{}</a>'.format( self.DS_URL[ self.type ], self.type )
		page_data[ "dev_info"    ]	= info
		page_data[ "mcu"         ]	= os.uname().machine
		page_data[ "n_ch"        ]	= str( count )
		page_data[ "pwm0_idx"    ]	= str( pwm0_idx )
		page_data[ "iref0_idx"   ]	= str( iref0_idx )
		page_data[ "pwmall_idx"  ]	= str( pwmall_idx )
		page_data[ "irefall_idx" ]	= str( irefall_idx )
		page_data[ "iref_ofst"   ]	= str( self.IREF_ID_OFFSET )
		page_data[ "iref_init"   ]	= str( self.IREF_INIT )
		page_data[ "reg_table"   ]	= self.get_reg_table( self.dev, 4 )
		page_data[ "allreg_note" ]	= allreg_note

		cols		= 4	if all_reg else 1

		page_data[ "sliders_PWM"  ]	= self.get_slider_table( cols, col_pat, iref = False, all_reg = all_reg )
		
		if iref:
			page_data[ "sliders_IREF" ]	= self.get_slider_table( cols, col_pat, iref = True, all_reg = all_reg )
		else:
			page_data[ "sliders_IREF" ]	= ""

		files	= {	"css": 	[	"demo_lib/general"	],
					"js":	[	"demo_lib/general",
								"demo_lib/" + self.__class__.__name__
							]
					}
		
		html	= utils.file_loading( html, files )
		
		for key, value in page_data.items():
			html = html.replace('{% ' + key + ' %}', value )
		
		return html

	def get_slider_table( self, cols, pat, iref, all_reg = False ):
		rows	= (self.dev.CHANNELS + cols - 1) // cols
		label	= "IREF" if iref else "PWM"
		c		= { "R": "#FF0000", "G": "#008000", "B": "#0000FF", "K": "#000000" }
		cs		= { "R": "item_R",  "G": "item_G",  "B": "item_B",  "K": "item_K"  }
		template	= [	'<font color={}>{}</font>',
						'<input type="range" oninput="updateSlider( this, 1, {} )" onchange="updateSlider( this, 0, {} )" id="Slider{}" min="0" max="255" step="1" value="0" class="slider">',
						'<input type="text" onchange="updateValField( this, {} )" id="valField{}" minlength=2 size=2 value="00"">'
						]

		s	 	= [ '<table class="table_LEDC">' ]

		for y in range( rows ):
			s	 	+= [ '<tr class="slider_table_row">' ]
			for i in range( y, self.dev.CHANNELS, rows ):
				id	 = i + (self.IREF_ID_OFFSET if iref else 0)
				s	+= [ self.table_item( template, i, id, c[ pat[ i ] ], cs[ pat[ i ] ], label + str( i ) ) ]

			s	+= [ '</tr>' ]

		if all_reg:
			i		 = (self.IREF_ID_OFFSET - 1)
			id	 	 = i + (self.IREF_ID_OFFSET if iref else 0)

			s	+= [ '<tr class="slider_table_row">' ]
			s	+= [ self.table_item( template, i, id, c[ "K" ], cs[ "K" ], label + "ALL" ) ]
			s	+= [ '</tr>' ]

		s	+= [ '</table>' ]
		return "\n".join( s )

	def table_item( self, template, i, id, c_l, cs_l, label ):
		s	 = [ '<td align ="right" class="{} td_LEDC">'.format( cs_l ) ]
		s	+= [ template[ 0 ].format( c_l, label ) ]
		s	+= [ '</td><td class="{} td_LEDC">'.format( cs_l ) ]
		s	+= [ template[ 1 ].format( id, id, id ) ]
		s	+= [ '</td><td class="{} td_LEDC">'.format( cs_l ) ]
		s	+= [ template[ 2 ].format( id, id ) ]
		s	+= [ '</td>' ]

		return "\n".join( s )

	def get_reg_table( self, dev, cols ):
		total	= len( dev.REG_NAME )
		rows	= (total + cols - 1) // cols

		s	 	= [ '<table class="table_LEDC">' ]

		for y in range( rows ):
			s	 	+= [ '<tr class="reg_table_row">' ]
			for i in range( y, total, rows ):
				s	+= [ '<td class="reg_table_name td_LEDC">{}</td><td class="reg_table_val td_LEDC">0x{:02X}</td>'.format( dev.REG_NAME[ i ], i ) ]
				s	+= [ '<td class="reg_table_val td_LEDC"><input type="text" onchange="updateRegField( this, {} )" id="regField{}" minlength=2 size=2 value="--" class="regfield"></td>'.format( i, i ) ]

			s	+= [ '</tr>' ]

		s	+= [ '</table>' ]
		return "\n".join( s )
