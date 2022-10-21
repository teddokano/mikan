#	MicroPython HTTP server sample code based on "http_server_simplistic.py".
#	https://github.com/micropython/micropython/blob/master/examples/network/http_server_simplistic.py
#
#
#	Based on simple HTTP server code, Trying LED ON/OFF via web
#	https://gist.github.com/teddokano/45b99cd906e63a23105ab427ae70d1dc
#	https://forum.micropython.org/viewtopic.php?t=1940#p10926
#
#	Imprementing slider interface
#	https://randomnerdtutorials.com/esp32-web-server-slider-pwm/
#	https://developer.mozilla.org/ja/docs/Web/CSS/::-webkit-slider-thumb
#	https://code-kitchen.dev/html/input-range/
#	https://memorva.jp/memo/mobile/sp_viewport.php
#
#	HTML modification
#	https://1-notes.com/python-replace-html/
#
#	Tedd OKANO / Released under the MIT license
#	15-Oct-2022
#	version	0.1

import	network
import	ujson
import	machine
import	os
import	ure

from	nxp_periph	import	PCA9956B, PCA9955B, PCA9632, PCA9957, LED

try:
    import usocket as socket
except:
    import socket




front_page = """\
HTTP/1.0 200 OK

<!DOCTYPE html>
<html>
	<head>
		<meta charset="utf-8" />
		<title>test</title>
	</head>
	<body>
		<a href = "/PCA9955B">test page</a>
	</body>
</html>
"""



def main( micropython_optimize=False ):


	dut	= DUT_LEDC()









	ip_info	= start_network()

	s = socket.socket()

	ai = socket.getaddrinfo( "0.0.0.0", 8080 )
	addr = ai[0][-1]

	s.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
	s.bind( addr )
	s.listen( 5 )
	print("Listening, connect your browser to http://{}:8080/".format( ip_info[0] ))

	while True:
		res = s.accept()
		client_sock = res[0]
		client_addr = res[1]
		print("Client address:", client_addr)
		print("Client socket:", client_sock)

		if not micropython_optimize:
			client_stream = client_sock.makefile("rwb")
		else:
			client_stream = client_sock

		req = client_stream.readline()
		print( "Request: {}".format( req.decode() ) )

		html	= dut.parse( req )

		if html is None:
			html	= front_page

		while True:
			h = client_stream.readline()
			if h == b"" or h == b"\r\n":
				break
			#print(h)
		
		print( html )
		client_stream.write( html )

		client_stream.close()
		if not micropython_optimize:
			client_sock.close()
		print()

def start_network( port = 0, ifcnfg_param = "dhcp" ):
	print( "starting network" )

	lan = network.LAN( port )
	lan.active( True )

	print( "ethernet port %d is activated" % port )

	lan.ifconfig( ifcnfg_param )
	return lan.ifconfig()
	


		



class DUT_LEDC():
	IREF_INIT	= 0x10
	regex_pwm	= ure.compile( r".*value=(\d+)&idx=(\d+)" )
	regex_reg	= ure.compile( r".*reg=(\d+)&val=(\d+)" )

	IREF_ID_OFFSET	= 100

	def __init__( self ):
		self.interface	= machine.I2C( 0, freq = (400 * 1000) )
		self.dev		= PCA9955B( self.interface, address = 0x02 >> 1, iref = self.IREF_INIT )
		self.led		= [ LED( self.dev, i ) for i in range( self.dev.CHANNELS ) ]
		self.dev_name	= self.dev.__class__.__name__

	def parse( self, req ):
		print( "!!!! %s: <--- request ---- \"%s\"" % ( self.dev_name, req.decode() ) )
		if self.dev_name not in req:
			return
	
		print( "parsing: %s" % req )
	
		if "?" not in req:
			html	= self.page_setup()

			if "PCA9632" not in self.dev.info():
				self.dev.write_registers( "IREFALL", self.IREF_INIT )

			for i in range( self.dev.CHANNELS ):
				self.led[ i ].v	= 0.0
		elif "allreg" in req:
			html	= 'HTTP/1.0 200 OK\n\n' + ujson.dumps( { "reg": self.dev.dump() } )
		else:
			html	= 'HTTP/1.0 200 OK\n\n'	# dummy

			m	= self.regex_pwm.match( req )
			if m:
				print( m.groups() )
				pwm	= int( m.group( 1 ) )
				ch	= int( m.group( 2 ) )
				
				if ch < (self.IREF_ID_OFFSET - 1):
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
				print( m.groups() )
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
				{% style %}
			</head>
			<body>
				<script>
					const	DEV_NAME	= '{% dev_name %}';
					const	N_CHANNELS	= {% n_ch %};
					const	IREF_OFST	= {% iref_ofst %};
					const	IREF_INIT	= {% iref_init %};
					const	REQ_HEADER	= '/' + DEV_NAME + '?';
					
					/****************************
					 ****	slider controls
					 ****************************/
					 
					let timeoutId	= null;

					/******** updateSlider ********/

					function updateSlider( element, moving, idx ) {
						let value = document.getElementById( "Slider" + idx ).value;
						
						setSliderValues( idx, value );

						if ( moving ) {
							//	thinning out events		//	https://lab.syncer.jp/Web/JavaScript/Snippet/43/
							if ( timeoutId ) return ;
							timeoutId = setTimeout( function () { timeoutId = 0; }, 50 );
						}
						
						console.log( 'pwm' + idx + ': ' + value + ', moving?: ' + moving );

						let url	= REQ_HEADER + 'value=' + value + '&idx=' + idx
						ajaxUpdate( url )
					}
					
					function updateSliderDone() {
						let obj = JSON.parse( this.responseText );
						setSliderValues( obj.idx, obj.value );
					}
					
					/******** updateValField ********/

					function updateValField( element, idx ) {
						let valueFieldElement = document.getElementById( "valField" + idx );
						let value	= parseInt( valueFieldElement.value, 16 )
						let no_submit	= 0
						
						if ( isNaN( value ) ) {
							no_submit	= 1
							value = document.getElementById( "Slider" + idx ).value;
						}
						value	= (value < 0  ) ?   0 : value
						value	= (255 < value) ? 255 : value
						valueFieldElement.value = hex( value )

						if ( no_submit )
							return;

						setSliderValues( idx, value );
						console.log( 'pwm' + idx + ': ' + value );
						
						let url	= REQ_HEADER + 'value=' + value + '&idx=' + idx
						ajaxUpdate( url )
					}
					
					/******** setSliderValues ********/

					function setSliderValues( i, value ) {
						document.getElementById( "Slider" + i ).value = value;
						document.getElementById( "valField" + i ).value = hex( value )

						if ( i == (IREF_OFST - 1) )
							setAllSliderValues( 0, N_CHANNELS, value );
						else if ( i == (IREF_OFST* 2 - 1) )
							setAllSliderValues( IREF_OFST, N_CHANNELS, value );
					}
					
					/******** setAllSliderValues ********/

					function setAllSliderValues( start, length, value ) {
						for ( let i = start; i < start + length; i++ ) {
							document.getElementById( "Slider" + i ).value = value;
							document.getElementById( "valField" + i ).value = hex( value )
						}
					}
					

					
					/****************************
					 ****	register controls
					 ****************************/
					 
					/******** updateRegField ********/

					function updateRegField( element, idx ) {
						let valueFieldElement = document.getElementById( "regField" + idx );
						let value	= parseInt( valueFieldElement.value, 16 )
						let no_submit	= 0
						
						if ( isNaN( value ) ) {
							no_submit	= 1
							value = document.getElementById( "Slider" + idx ).value;
						}
						value	= (value < 0  ) ?   0 : value
						value	= (255 < value) ? 255 : value
						valueFieldElement.value = hex( value )

						if ( no_submit )
							return;

						let url	= REQ_HEADER + 'reg=' + idx + '&val=' + value
						ajaxUpdate( url, updateRegFieldDone )
					}
					
					function updateRegFieldDone() {
						let obj = JSON.parse( this.responseText );
						
						document.getElementById('regField' + obj.reg ).value	= hex( obj.val )
					}

					/******** allRegLoad ********/

					function allRegLoad() {
						let url	= REQ_HEADER + 'allreg='
						ajaxUpdate( url, allRegLoadDone );
					}

					/******** allRegLoadDone ********/

					function allRegLoadDone() {
						let obj = JSON.parse( this.responseText );

						for ( let i = 0; i < obj.reg.length; i++ ) {
							document.getElementById('regField' + i ).value	= hex( obj.reg[ i ] )
						}
					}
					
					
					
					/****************************
					 ****	page load controls
					 ****************************/
					 
					function loadFinished(){
						setAllSliderValues( IREF_OFST, N_CHANNELS, IREF_INIT );
						setAllSliderValues( IREF_OFST * 2 - 1, 1, IREF_INIT );
						allRegLoad();
					}

					window.addEventListener('load', loadFinished);



					/****************************
					 ****	service routine
					 ****************************/
					 
					/******** ajaxUpdate ********/

					function ajaxUpdate( url, func ) {
						url			= url + '?ver=' + new Date().getTime();
						let	ajax	= new XMLHttpRequest;
						ajax.open( 'GET', url, true );
						
						ajax.onload = func;
						ajax.send( null );
					}
					
					function hex( num ) {
						return ('00' + Number( num ).toString( 16 ).toUpperCase()).slice( -2 )
					}

				</script>

				<div class="header">
					<p>{% dev_name %} server</p>
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
					<div aligh=left><input type="button" onclick="allRegLoad();" value="load" class="all_reg_load"></div>
				</div>
				
				<div class="foot_note">
					<b>HTTP server on<br/>
					{% mcu %}</b><br/>
					0100111101101011011000010110111001101111
				</div>
		</body>
		</html>
		"""
		
		page_data	= {}
		page_data[ "dev_name"  ]	= self.dev_name
		page_data[ "dev_info"  ]	= self.dev.info()
		page_data[ "mcu"       ]	= os.uname().machine
		page_data[ "n_ch"      ]	= str( self.dev.CHANNELS )
		page_data[ "iref_ofst" ]	= str( self.IREF_ID_OFFSET )
		page_data[ "iref_init" ]	= str( self.IREF_INIT )
		page_data[ "style"     ]	= self.get_style()
		page_data[ "reg_table" ]	= self.get_reg_table( self.dev, 4 )

		count	= self.dev.CHANNELS
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
		#cols		= 4	if led_c.CHANNELS % 3 else 3
		cols		= 4	if all_reg else 1

		page_data[ "sliders_PWM"  ]	= self.get_slider_table( cols, col_pat, iref = False, all_reg = all_reg )
		
		if iref:
			page_data[ "sliders_IREF" ]	= self.get_slider_table( cols, col_pat, iref = True, all_reg = all_reg )
		else:
			page_data[ "sliders_IREF" ]	= ""

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

		s	 	= [ '<table>' ]

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
		s	 = [ '<td align ="right" class="{}">'.format( cs_l ) ]
		s	+= [ template[ 0 ].format( c_l, label ) ]
		s	+= [ '</td><td class="{}">'.format( cs_l ) ]
		s	+= [ template[ 1 ].format( id, id, id ) ]
		s	+= [ '</td><td class="{}">'.format( cs_l ) ]
		s	+= [ template[ 2 ].format( id, id ) ]
		s	+= [ '</td>' ]

		return "\n".join( s )

	def get_reg_table( self, dev, cols ):
		total	= len( dev.REG_NAME )
		rows	= (total + cols - 1) // cols

		s	 	= [ '<table>' ]

		for y in range( rows ):
			s	 	+= [ '<tr class="reg_table_row">' ]
			for i in range( y, total, rows ):
				s	+= [ '<td class="reg_table_name">{}</td><td class="reg_table_val">0x{:02X}</td>'.format( dev.REG_NAME[ i ], i ) ]
				s	+= [ '<td  class="reg_table_val"><input type="text" onchange="updateRegField( this, {} )" id="regField{}" minlength=2 size=2 value="--" class="regfield"></td>'.format( i, i ) ]

			s	+= [ '</tr>' ]

		s	+= [ '</table>' ]
		return "\n".join( s )

	def get_style( self ):
		s	= """\
		<style>
		html {
			font-size: 80%;
			font-family: Arial;
			display: inline-block;
			text-align: center;
		}
		body {
			font-size: 1.0rem;
			font-color: #000000;
			vertical-align: middle;
		}
		div {
			border: solid 1px #EEEEEE;
			box-sizing: border-box;
			text-align: center;
			font-size: 1.5rem;
			padding: 5px;
		}
		.header {
			border: solid 1px #EEEEEE;
			text-align: center;
			font-size: 1.5rem;
			padding: 1.0rem;
		}
		.info {
			text-align: center;
			font-size: 1.0rem;
		}
		.control_panel {
			box-sizing: border-box;
			text-align: left;
			font-size: 1.0rem;
		}
		.slider_table_row {
			height: 3.0rem;
		}
		.item_R {
			background-color: #FFEEEE;
		}
		.item_G {
			background-color: #EEFFEE;
		}
		.item_B {
			background-color: #EEEEFF;
		}
		.reg_table {
			box-sizing: border-box;
			text-align: left;
			font-size: 1.0rem;
		}
		.reg_table_row {
			height: 1.0rem;
		}
		.foot_note {
			text-align: center;
			font-size: 1rem;
			padding: 0.5rem;
		}
		
		input[type="range"] {
			-webkit-appearance: none;
			appearance: none;
			cursor: pointer;
			outline: none;
			height: 5px; width: 85%;
			background: #E0E0E0;
			border-radius: 10px;
			border: solid 3px #C0C0C0;
		}
		input[type="range"]::-webkit-slider-thumb {
			-webkit-appearance: none;
			background: #707070;
			width: 20px;
			height: 20px;
			border-radius: 50%;
			box-shadow: 0px 3px 6px 0px rgba(0, 0, 0, 0.15);
		}
		input[type="range"]:active::-webkit-slider-thumb {
			box-shadow: 0px 5px 10px -2px rgba(0, 0, 0, 0.3);
		}
		input[type="text"] {
			width: 2em;
			height: 1em;
			font-size: 100%;
		}
		table {
			background-color: #EEEEEE;
			border-collapse: collapse;
			width: 100%;
		}
		td {
			border: solid 1px #FFFFFF;
			text-align: center;
		}
		</style>
		"""
		return s

main()


