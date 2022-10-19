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

IREF_INIT	= 0x10
regex_pwm	= ure.compile( r".*value=(\d+)&idx=(\d+)" )
regex_reg	= ure.compile( r".*reg=(\d+)&val=(\d+)" )

IREF_ID_OFFSET	= 100

interface	= machine.I2C( 0, freq = (400 * 1000) )
led_c		= PCA9955B( interface, address = 0x02 >> 1, iref = IREF_INIT )
#led_c		= PCA9632( interface )
"""
interface	= machine.SPI( 0, 1000 * 1000, cs = 0 )
led_c		= PCA9957( interface, setup_EVB = True, iref = IREF_INIT )
"""

led			= [ LED( led_c, i ) for i in range( led_c.CHANNELS ) ]

def main( micropython_optimize=False ):
	ip_info	= start_network()

	s = socket.socket()

	ai = socket.getaddrinfo( "0.0.0.0", 8080 )
	addr = ai[0][-1]

	s.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
	s.bind( addr )
	s.listen( 1 )
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

		print("Request:")
		req = client_stream.readline()
		print( req )
		
		if "?" not in req:
			html	= page_setup( led_c )

			if "PCA9632" not in led_c.info():
				led_c.write_registers( "IREFALL", IREF_INIT )

			for i in range( led_c.CHANNELS ):
				led[ i ].v	= 0.0
		elif "allreg" in req:
			html	= 'HTTP/1.0 200 OK\n\n' + ujson.dumps( { "reg": led_c.dump(), "str": "test message" } )
			print( html )
		else:
			m	= regex_pwm.match( req )
			if m:
				print( m.groups() )
				pwm	= int( m.group( 1 ) )
				ch	= int( m.group( 2 ) )
				
				if ch < (IREF_ID_OFFSET - 1):
					led[ ch ].v	= pwm / 255
				elif ch is (IREF_ID_OFFSET - 1):
					led_c.write_registers( "PWMALL", pwm )
				elif ch < (IREF_ID_OFFSET * 2 - 1):
					led[ ch - IREF_ID_OFFSET ].i	= pwm / 255
				elif ch is (IREF_ID_OFFSET * 2 - 1):
					led_c.write_registers( "IREFALL", pwm )
				else:
					pass

			m	= regex_reg.match( req )
			if m:
				print( m.groups() )
				reg	= int( m.group( 1 ) )
				val	= int( m.group( 2 ) )

				led_c.write_registers( reg, val )

				html	= 'HTTP/1.0 200 OK\n\n' + ujson.dumps( { "reg": reg, "val": val } )

		while True:
			h = client_stream.readline()
			if h == b"" or h == b"\r\n":
				break
			#print(h)
#		client_stream.read()
					
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
	

def page_setup( led_c ):
	#HTML to send to browsers
	html = """\
	HTTP/1.0 200 OK

	<!DOCTYPE html>
	<html>
		<head>
			<title>{% dev_name %} server</title>
			{% style %}
		</head>
		<body>
			<script>
			
				/****************************
				 ****	slider controls
				 ****************************/
				 
				var timeoutId	= null;

				/******** updateSlider ********/

				function updateSlider( element, moving, idx ) {
					var value = document.getElementById( "Slider" + idx ).value;
					document.getElementById( "valField" + idx ).value = hex( value )

					if ( moving ) {
						//	thinning out events		//	https://lab.syncer.jp/Web/JavaScript/Snippet/43/
						if ( timeoutId ) return ;
						timeoutId = setTimeout( function () { timeoutId = 0; }, 50 );
					}
					
					if ( idx == ({% iref_ofst %} - 1) )
						setSliderValues( 0, {% num_ch %}, value );

					if ( idx == ({% iref_ofst %} * 2 - 1) )
						setSliderValues( {% iref_ofst %}, {% num_ch %}, value );

					console.log( 'pwm' + idx + ': ' + value + ', moving?: ' + moving );

					var url	= "/{% dev_name %}?value=" + value + "&idx=" + idx
					ajaxUpdate( url )
				}
				
				/******** updateValField ********/

				function updateValField( element, idx ) {
					var valueFieldElement = document.getElementById( "valField" + idx );
					var value	= parseInt( valueFieldElement.value, 16 )
					var no_submit	= 0
					
					if ( isNaN( value ) ) {
						no_submit	= 1
						value = document.getElementById( "Slider" + idx ).value;
					}
					value	= (value < 0  ) ?   0 : value
					value	= (255 < value) ? 255 : value
					valueFieldElement.value = hex( value )

					if ( no_submit )
						return;

					document.getElementById( "Slider" + idx ).value = value;
					
					if ( idx == ({% iref_ofst %} - 1) )
						setSliderValues( 0, {% num_ch %}, value );

					if ( idx == ({% iref_ofst %} * 2 - 1) )
						setSliderValues( {% iref_ofst %}, {% num_ch %}, value );

					console.log( 'pwm' + idx + ': ' + value );
					
					var url	= "/{% dev_name %}?value=" + value + "&idx=" + idx
					ajaxUpdate( url )
				}
				
				/******** setSliderValues ********/

				function setSliderValues( start, length, value ) {
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
					var valueFieldElement = document.getElementById( "regField" + idx );
					var value	= parseInt( valueFieldElement.value, 16 )
					
					var url	= "/{% dev_name %}?reg=" + idx + "&val=" + value
					ajaxUpdate( url, updateRegFieldDone )
				}
				
				function updateRegFieldDone() {
					obj = JSON.parse( this.responseText );
					
					document.getElementById('regField' + obj.reg ).value	= hex( obj.val )
				}

				/******** allRegLoad ********/

				function allRegLoad() {
					ajaxUpdate( 'allreg', allRegLoadDone );
				}

				/******** allRegLoadDone ********/

				function allRegLoadDone() {
					obj = JSON.parse( this.responseText );

					for ( let i = 0; i < obj.reg.length; i++ ) {
						document.getElementById('regField' + i ).value	= hex( obj.reg[ i ] )
					}
				}
				
				
				
				/****************************
				 ****	page load controls
				 ****************************/
				 
				function loadFinished(){
					setSliderValues( {% iref_ofst %}, {% num_ch %}, {% iref_init %} );
					setSliderValues( {% iref_ofst %} * 2 - 1, 1, {% iref_init %} );
					allRegLoad();
				}

				window.addEventListener('load', loadFinished);



				/****************************
				 ****	service routine
				 ****************************/
				 
				/******** ajaxUpdate ********/

				function ajaxUpdate( url, func ) {
					url			= url + '?ver=' + new Date().getTime();
					var	ajax	= new XMLHttpRequest;
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
	page_data[ "dev_name"  ]	= led_c.__class__.__name__
	page_data[ "dev_info"  ]	= led_c.info()
	page_data[ "mcu"       ]	= os.uname().machine
	page_data[ "ch-offset" ]	= "".join( [ '<option value="{}">{}</option>'.format( i, i ) for i in range( 0, led_c.CHANNELS, 3 ) ] )
	page_data[ "num_ch"    ]	= str( led_c.CHANNELS )
	page_data[ "iref_ofst" ]	= str( IREF_ID_OFFSET )
	page_data[ "iref_init" ]	= str( IREF_INIT )
	page_data[ "style"     ]	= get_style()
	page_data[ "reg_table" ]	= get_reg_table( led_c, 4 )

	count	= led_c.CHANNELS
	info	= led_c.info()
	
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

	iref		= hasattr( led_c, "__iref_base" )
	#cols		= 4	if led_c.CHANNELS % 3 else 3
	cols		= 4	if all_reg else 1

	page_data[ "sliders_PWM"  ]	= get_slider_table( led_c.CHANNELS, cols, col_pat, iref = False, all_reg = all_reg )
	
	if iref:
		page_data[ "sliders_IREF" ]	= get_slider_table( led_c.CHANNELS, cols, col_pat, iref = True, all_reg = all_reg )
	else:
		page_data[ "sliders_IREF" ]	= ""

	for key, value in page_data.items():
		html = html.replace('{% ' + key + ' %}', value )
	
	return html

def get_slider_table( total, cols, pat, iref, all_reg = False ):
	rows	= (total + cols - 1) // cols
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
		for i in range( y, total, rows ):
			id	 = i + (IREF_ID_OFFSET if iref else 0)
			s	+= [ table_item( template, i, id, c[ pat[ i ] ], cs[ pat[ i ] ], label + str( i ) ) ]

		s	+= [ '</tr>' ]

	if all_reg:
		i		 = (IREF_ID_OFFSET - 1)
		id	 	 = i + (IREF_ID_OFFSET if iref else 0)

		s	+= [ '<tr class="slider_table_row">' ]
		s	+= [ table_item( template, i, id, c[ "K" ], cs[ "K" ], label + "ALL" ) ]
		s	+= [ '</tr>' ]

	s	+= [ '</table>' ]
	return "\n".join( s )

def table_item( template, i, id, c_l, cs_l, label ):
	s	 = [ '<td align ="right" class="{}">'.format( cs_l ) ]
	s	+= [ template[ 0 ].format( c_l, label ) ]
	s	+= [ '</td><td class="{}">'.format( cs_l ) ]
	s	+= [ template[ 1 ].format( id, id, id ) ]
	s	+= [ '</td><td class="{}">'.format( cs_l ) ]
	s	+= [ template[ 2 ].format( id, id ) ]
	s	+= [ '</td>' ]

	return "\n".join( s )

def get_reg_table( dev, cols ):
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

def get_style():
	s	= """\
	<style>
	html {
		font-size: 100%;
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

