import	utime
import	ure
import	ujson

from	nxp_periph	import	PCA9956B, PCA9955B, PCA9632, PCA9957, LED
from	nxp_periph	import	LED_controller_base, gradation_control
from	demo_lib	import	DUT_base

class DUT_LEDC( DUT_base.DUT_base ):
	APPLIED_TO	= LED_controller_base
	IREF_INIT	= 0x10
	regex_pwm	= ure.compile( r".*value=(\d+)&idx=(\d+)" )
	regex_reg	= ure.compile( r".*reg=(\d+)&val=(\d+)" )
	regex_grch	= ure.compile( r".*gradation_settings=(.*)\?ver=.*" )
	regex_grss	= ure.compile( r".*gradation_start_stop=(.*)\?ver=.*" )
	
	DS_URL		= { "PCA9956B": "https://www.nxp.com/docs/en/data-sheet/PCA9956B.pdf",
					"PCA9955B": "https://www.nxp.com/docs/en/data-sheet/PCA9955B.pdf",
					"PCA9632": "https://www.nxp.com/docs/en/data-sheet/PCA9632.pdf",
					"PCA9957": "https://www.nxp.com/docs/en/data-sheet/PCA9957DS.pdf"
					}

	def __init__( self, dev ):
		super().__init__( dev )
		self.led		= [ LED( self.dev, i ) for i in range( self.dev.CHANNELS ) ]
		self.info		= [ "LED controller", "{}ch".format( self.dev.CHANNELS ) ]
		self.symbol		= '💡'

		self.page_data[ "symbol" ]	= self.symbol
		if hasattr( self.dev, "__iref_base" ):
			self.IREF_ID_OFFSET	= 100
			#self.dev.write_registers( "IREFALL", self.IREF_INIT )
		else:
			self.IREF_ID_OFFSET	= 0
			
		if "PCA9957" in self.dev.info():
			self.dev.bit_operation( "MODE2", 0x18, 0x18 )

	def parse( self, req ):
		#print( "!!!! %s: <--- request ---- \"%s\"" % ( self.dev_name, req.decode() ) )
		if self.dev_name not in req:
			return None
	
		if "?" not in req:
#			for i in range( self.dev.CHANNELS ):
#				self.led[ i ].v	= 0.0

			return	self.page_setup()

		elif "allreg" in req:
			return ujson.dumps( { "reg": self.dev.dump() } )
		else:
			html	= ""	# dummy

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

				return ujson.dumps( { "val": pwm, "idx": ch } )

			m	= self.regex_reg.match( req )
			if m:
				#print( m.groups() )
				reg	= int( m.group( 1 ) )
				val	= int( m.group( 2 ) )

				self.dev.write_registers( reg, val )

				return ujson.dumps( { "reg": reg, "val": val } )

			m	= self.regex_grch.match( req )
			if m:
				obj	= ujson.loads( bytearray( m.group( 1 ).decode().replace( '%22', '"' ), "utf-8" ) )

				self.dev.gradation_channel_enable( obj[ "channels" ] )
				self.dev.gradation_group_assign( obj[ "group" ] )
				
				for i, r in enumerate( obj[ "regs" ] ):
					self.dev.write_registers( "RAMP_RATE_GRP{}".format( i ), r )
					
				return ujson.dumps( { "reg": self.dev.dump() } )

			m	= self.regex_grss.match( req )
			if m:
				obj	= ujson.loads( bytearray( m.group( 1 ).decode().replace( '%22', '"' ), "utf-8" ) )
				
				if ( obj[ "start" ] ):
					timing_list	= sorted( obj[ "grps" ].keys() )
					
					prev_t	= 0.0
					for t in timing_list:
						timing	= float( t )
						utime.sleep( timing - prev_t )
						prev_t	= timing
						print( "gradation control: starting group: {}".format( obj[ "grps" ][ t ] ) )
						self.dev.gradation_start( obj[ "grps" ][ t ], continuous = True if (obj[ "start" ] == 1) else False )
						
				else:
					print( obj[ "grps" ] )
					if any( obj[ "grps" ] ):
						self.dev.gradation_stop( obj[ "grps" ][ "0" ] )
				
				html	= ujson.dumps( { "reg": self.dev.dump() } )

	def page_setup( self ):
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
		irefall_idx	= self.dev.REG_NAME.index( "IREFALL" ) if all_reg else 0
		
		if all_reg:
			if irefall_idx:
				allreg_note	= "PWMAALL and IREFALL are write-only register. ignore loaded value"
			else:
				allreg_note	= "PWMAALL is a write-only register. ignore loaded value"
		else:
				allreg_note	= ""

		self.page_data[ "grad_ctrl"   ]	= self.grad_ctrl() if issubclass( self.dev.__class__, gradation_control ) else ""
		self.page_data[ "n_ch"        ]	= str( self.dev.CHANNELS )
		self.page_data[ "pwm0_idx"    ]	= str( self.dev.REG_NAME.index( "PWM0"  ) )
		self.page_data[ "iref0_idx"   ]	= str( self.dev.REG_NAME.index( "IREF0" ) if iref else 0 )
		self.page_data[ "pwmall_idx"  ]	= str( self.dev.REG_NAME.index( "PWMALL"  ) if all_reg else 0 )
		self.page_data[ "irefall_idx" ]	= str( irefall_idx )
		self.page_data[ "iref_ofst"   ]	= str( self.IREF_ID_OFFSET )
		self.page_data[ "iref_init"   ]	= str( self.IREF_INIT )
		self.page_data[ "reg_table"   ]	= self.get_reg_table( self.dev, 4 )
		self.page_data[ "allreg_note" ]	= allreg_note

		cols		= 4	if all_reg else 1

		self.page_data[ "sliders_PWM"  ]	= self.get_slider_table( cols, col_pat, iref = False, all_reg = all_reg )
		
		if iref:
			self.page_data[ "sliders_IREF" ]	= self.get_slider_table( cols, col_pat, iref = True, all_reg = all_reg )
		else:
			self.page_data[ "sliders_IREF" ]	= ""
		
		return self.load_html()
		
	def get_slider_table( self, cols, pat, iref, all_reg = False ):
		rows	= (self.dev.CHANNELS + cols - 1) // cols
		label	= "IREF" if iref else "PWM"
		c		= { "R": "#FF0000", "G": "#008000", "B": "#0000FF", "K": "#000000" }
		cs		= { "R": "item_R",  "G": "item_G",  "B": "item_B",  "K": "item_K"  }
		template	= [	'<font color={}>{}</font>',
						'<input type="range" oninput="updateSlider( 1, \'Slider\', {} )" onmouseup="updateSlider( 0, \'Slider\', {} )" id="Slider{}" min="0" max="255" step="1" value="0" class="slider">',
						'<input type="text" onchange="updateValField( \'valField\', {} )" id="valField{}" minlength=2 size=2 value="00">'
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
				s	+= [ '<td class="reg_table_val td_LEDC"><input type="text" onchange="updateValField( \'regField\', {} )" id="regField{}" minlength=2 size=2 value="--" class="regfield"></td>'.format( i, i ) ]

			s	+= [ '</tr>' ]

		s	+= [ '</table>' ]
		return "\n".join( s )

	def grad_ctrl( self ):
		s	= [ '<script>const GRAD_GRPS = {};\n</script>'.format( self.dev.GRAD_GRPS ) ]
		
		t	= """\
				<div id="reg_table" class="control_panel reg_table">
					<canvas id="myLineChart" width="40" height="10"></canvas>
					<!-- <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.7.2/Chart.bundle.js"></script> -->
					<script async src="jslib/chart.umd.js"></script>


				<div id="reg_table" class="control_panel reg_table">
				Gradation enable (IREF value is controlled by gradation)<br/>
				<input type="button" onclick="gradationEnable( 1 );"  value="Check all" class="tmp_button">
				<input type="button" onclick="gradationEnable( 0 );"  value="Clear all" class="tmp_button">
				<input type="button" onclick="gradationEnable( -1 );" value="Demo preset"  class="tmp_button">
				<table class="table_LEDC">
				<tr>
				"""
		s	+= [ t ]

		rows	= (self.dev.CHANNELS + 8 - 1) // 8
		
		for y in range( rows ):
			s	 	+= [ '<tr class="slider_table_row">' ]
			for i in range( y, self.dev.CHANNELS, rows ):
				s	+= [ '<td class="reg_table_name td_LEDC"><input type="checkbox" onchange="updatePlot();" id="gradationEnable{}">'. format( i ) ]
				s	+= [ '<label for="gradationEnable{}">ch {}</label></td>'.format( i, i ) ]
		
		t	= """
				</tr>
				</table></div>
				<div id="reg_table" class="control_panel reg_table">
				Group select<br/>
				<table class="table_LEDC">
				"""
		s	+= [ t ]

		for y in range( rows ):
			s	 	+= [ '<tr class="slider_table_row">' ]
			for i in range( y, self.dev.CHANNELS, rows ):
				s	+= [ '<td class="reg_table_name td_LEDC"><label for="groupSelect{}">ch {}</label><select name="group" id="groupSelect{}" oninput="updatePlot();">'.format( i, i, i ) ]
				s	+= [ '<option value="0">0</option><option value="1">1</option><option value="2">2</option><option value="3">3</option><option value="4">4</option><option value="5">5</option></select></td>' ]

			s	 	+= [ '</tr>' ]
					
		t	= """
				</tr>
				</table></div>
				<div id="reg_table" class="control_panel reg_table">
				Ramp setting<br/>
				<table class="table_LEDC">
				"""
		s	+= [ t ]

		tmp	= """\
				<tr>
					<td class="reg_table_name td_LEDC">
						{% grp %}
					</td>
					<td class="reg_table_name td_LEDC">
						<label for="maxCurrent{% grp %}">Max curent ratio</label>
						<input type="text" onchange="updatePlot();" id="maxCurrent{% grp %}" value="1.0" size=4>
					</td>
					<td class="reg_table_name td_LEDC">
						<label for="rampTimeField{% grp %}">Ramp-time</label>
						<input type="text" onchange="updatePlot();" id="rampTimeField{% grp %}" value="1.0" size=6>
					</td>
					<td class="reg_table_name td_LEDC">							
						<input type="checkbox" checked onchange="updatePlot();" id="rampSwUp{% grp %}">
						<label for="updateRampSwUp{% grp %}">Ramp-up</label>
					</td>
					<td class="reg_table_name td_LEDC">
						<input type="checkbox" checked onchange="updatePlot();" id="rampSwDown{% grp %}">
						<label for="updateRampSwDown{% grp %}">Ramp-down</label>
					</td>
					<td class="reg_table_name td_LEDC">
						<label for="updateHoldON{% grp %}">Hold-ON time</label>
						<select name="hold_on_time" id="holdON{% grp %}" oninput="updatePlot();">
							<option value="0.00">0.00</option>
							<option value="0.25">0.25</option>
							<option value="0.50">0.50</option>
							<option value="0.75">0.75</option>
							<option value="1.00">1.00</option>
							<option value="2.00">2.00</option>
							<option value="4.00">4.00</option>
							<option value="6.00">6.00</option>
						</select>
					</td>
					<td class="reg_table_name td_LEDC">
						<label for="updateHoldOFF{% grp %}">Hold-OFF time</label>
						<select name="hold_on_time" id="holdOFF{% grp %}" oninput="updatePlot();" value="1.00">
							<option value="0.00">0.00</option>
							<option value="0.25">0.25</option>
							<option value="0.50">0.50</option>
							<option value="0.75">0.75</option>
							<option value="1.00">1.00</option>
							<option value="2.00">2.00</option>
							<option value="4.00">4.00</option>
							<option value="6.00">6.00</option>
						</select>
					</td>
				</tr>
				"""

		for i in range( self.dev.GRAD_GRPS ):
			s	+= [ tmp.replace( '{% grp %}', str( i ) ) ]
		
		t	= """
				</table></div>
				<div id="reg_table" class="control_panel reg_table">
				Start / Stop control<br/>
				<input type="button" onclick="gradationStart( 1 );"  value="Start (continue)" class="tmp_button">
				<input type="button" onclick="gradationStart( 2 );"  value="Start (single shot)" class="tmp_button">
				<input type="button" onclick="gradationStart( 0 );"  value="Stop"  class="tmp_button">
				<input type="button" onclick="gradationStart( -1 );" value="All stop"  class="tmp_button">
				<table class="table_LEDC">
				"""
		s	+= [ t ]
		
		tmp	= """\
					<tr>
						<td class="reg_table_name td_LEDC">
							<input type="checkbox" checked id="startGrp{% grp %}">
							Start/Stop enable
						</td>
						<!--
						<td class="reg_table_name td_LEDC">
							<input type="checkbox" checked id="continueGrp{% grp %}">
							Continue
						</td>
						-->
						<td class="reg_table_name td_LEDC">
							<label for="startDelay{% grp %}">Start delay</label>
							<select id="startDelay{% grp %}" oninput="updatePlot();">
								<option value="0">0</option>
								<option disabled="disabled" >---</option>
								<option value="1/2">1/2 phase</option>
								<option disabled="disabled" >---</option>
								<option value="1/3">1/3 phase</option>
								<option value="2/3">2/3 phase</option>
								<option disabled="disabled" >---</option>
								<option value="1/4">1/4 phase</option>
								<option value="3/4">3/4 phase</option>
							</select>
						</td>
						<td class="reg_table_name td_LEDC">
							<input type="text" id="rampTimeActual{% grp %}" size=7 disabled>
							sec/ramp
						</td>
						<td class="reg_table_name td_LEDC">
							<input type="text" id="cycleTimeActual{% grp %}" size=7 disabled>
							sec/cycle
						</td>
						
					</tr>
				"""
				
		for i in range( self.dev.GRAD_GRPS ):
			s	+= [ tmp.replace( '{% grp %}', str( i ) ) ]

		t	= """\
				</table></div></div>
				"""
		s	+= [ t ]

		return "\n".join( s )
