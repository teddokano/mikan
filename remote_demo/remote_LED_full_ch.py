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

IREF_ID_OFFSET	= 100

interface	= machine.I2C( 0, freq = (400 * 1000) )
led_c		= PCA9956B( interface, address = 0x02 >> 1, iref = IREF_INIT )
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

	maax_sliders	= 6
	html	= page_setup( led_c, maax_sliders )

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
			if "PCA9632" not in led_c.info():
				led_c.write_registers( "IREFALL", IREF_INIT )

			for i in range( led_c.CHANNELS ):
				led[ i ].v	= 0.0
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
	

def page_setup( led_c, count_max ):
	#HTML to send to browsers
	html = """\
	HTTP/1.0 200 OK

	<!DOCTYPE html>
	<html>
		<head>
			<title>{% dev_name %} server</title>
			<style>
				html { font-family: Arial; display: inline-block; text-align: center; }
				h2 { font-size: 1.8rem; }
				p { font-size: 1.1rem; }
				body { margin:100px auto; padding-bottom: 25px; font-size: 0.8rem; }
				input[type="range"] { -webkit-appearance: none; appearance: none; cursor: pointer; outline: none; height: 5px; width: 80%; background: #E0E0E0; border-radius: 10px; border: solid 3px #C0C0C0; }
				input[type="range"]::-webkit-slider-thumb { -webkit-appearance: none; background: #707070; width: 20px; height: 20px; border-radius: 50%; box-shadow: 0px 3px 6px 0px rgba(0, 0, 0, 0.15); }
				input[type="range"]:active::-webkit-slider-thumb { box-shadow: 0px 5px 10px -2px rgba(0, 0, 0, 0.3); }
				input[type="text"] { width: 2em; height: 1em; font-size: 100%; }
				table { background-color: #EEEEEE; border-collapse: collapse; width: 100%; }
				th,td { border: solid 1px; color: #FFFFFF; }
			</style>
		</head>
		<body>
			<script>
				timeoutId	= null;
				function updateSlider( element, moving, idx ) {
					var sliderValue = document.getElementById( "Slider" + idx ).value;
					document.getElementById( "valField" + idx ).value = ('00' + Number( sliderValue ).toString( 16 )).slice( -2 )

					if ( moving ) {
						//	thinning out events		//	https://lab.syncer.jp/Web/JavaScript/Snippet/43/
						if ( timeoutId ) return ;
						timeoutId = setTimeout( function () { timeoutId = 0; }, 50 );
					}
					
					if ( idx == 99 ) {
						for ( let i = 0; i < 24; i++ ) {
							document.getElementById( "Slider" + i ).value = sliderValue;
							document.getElementById( "valField" + i ).value = ('00' + Number( sliderValue ).toString( 16 )).slice( -2 )
						}
					}

					console.log( 'pwm' + idx + ': ' + sliderValue + ', moving?: ' + moving );
					var xhr = new XMLHttpRequest();
					xhr.open("GET", "/slider?value=" + sliderValue + "&idx=" + idx, true);
					xhr.send();
				}
				
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
					valueFieldElement.value = ('00' + Number( value ).toString( 16 )).slice( -2 )

					//if ( no_submit )
					//	return;

					document.getElementById( "Slider" + idx ).value = value;
					console.log( 'pwm' + idx + ': ' + value );
					var xhr = new XMLHttpRequest();
					xhr.open("GET", "/slider?value=" + value + "&idx=" + idx, true);
					xhr.send();
				}
			</script>

			<h2>{% dev_name %} server</h2>
			PWM registers
			{% sliders_PWM %}
			IREF registers
			{% sliders_IREF %}

			<br/>HTTP server on <br>{% mcu %}<br/><br/>

			0100111101101011011000010110111001101111
		</body>
	</html>
	"""
	
	page_data	= {}
	page_data[ "dev_name"  ]	= led_c.__class__.__name__
	page_data[ "mcu"       ]	= os.uname().machine
	page_data[ "ch-offset" ]	= "".join( [ '<option value="{}">{}</option>'.format( i, i ) for i in range( 0, led_c.CHANNELS, 3 ) ] )

	count	= led_c.CHANNELS
	count	= count if count < count_max else count_max
	
	info		= led_c.info()
	separator	= 4 if ("PCA9955B" in info) or ("PCA9632" in info) else 3
	iref		= False if "PCA9632" in info else True
	cols		= 4	if led_c.CHANNELS % 3 else 3
	
	page_data[ "sliders_PWM"  ]	= get_slider_table( led_c.CHANNELS, cols, separator, iref = False, all_reg = True )
	page_data[ "sliders_IREF" ]	= get_slider_table( led_c.CHANNELS, cols, separator, iref = True,  all_reg = True  )

	for key, value in page_data.items():
		html = html.replace('{% ' + key + ' %}', value)
	
	return html

def get_slider_table( total, cols, separator, iref, all_reg = False ):
	rows	= (total + cols - 1) // cols
	label	= "IREF" if iref else "PWM"
	c		= [ "#FF0000", "#00FF00", "#0000FF", "#000000" ]
	cs		= [ "item_R", "item_G", "item_B", "item_K" ]
	template	= [	'<p><font color={}>{}</font></p>',
					'<p><input type="range" oninput="updateSlider( this, 1, {} )" onchange="updateSlider( this, 0, {} )" id="Slider{}" min="0" max="255" step="1" value="0" class="slider"></p>',
					'<p><input type="text" onchange="updateValField( this, {} )" id="valField{}" minlength=2 size=2 value="00" class="{}"></p>'
					]
					
	s	 	= [ '<table>' ]

	for y in range( rows ):
		s	 	+= [ '<tr>' ]
		for i in range( y, total, rows ):
			id	 = i + (IREF_ID_OFFSET if iref else 0)
			s	+= [ table_item( template, i, id, c[ i % separator ], cs[ i % separator ], label + str( i ) ) ]

		s	+= [ '</tr>' ]

	if all_reg:
		i		 = (IREF_ID_OFFSET - 1)
		id	 	 = i + (IREF_ID_OFFSET if iref else 0)

		s	+= [ '<tr>' ]
		s	+= [ table_item( template, i, id, c[ 3 ], cs[ 3 ], label + "ALL" ) ]
		s	+= [ '</tr>' ]

	s	+= [ '</table>' ]
	return "\n".join( s )

def table_item( template, i, id, c_l, cs_l, label ):
	s	 = [ '<td align ="left">' ]
	s	+= [ template[ 0 ].format( c_l, label ) ]
	s	+= [ '</td><td>' ]
	s	+= [ template[ 1 ].format( id, id, id ) ]
	s	+= [ '</td><td>' ]
	s	+= [ template[ 2 ].format( id, id, cs_l ) ]
	s	+= [ '</td>' ]

	return "\n".join( s )

main()
