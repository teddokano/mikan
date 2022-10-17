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
				
				if ch is 99:
					led_c.write_registers( "IREFALL", pwm )
				else:
					led[ ch ].v	= pwm / 255

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
			<meta name="viewport"
				content="width=320, height=480, initial-scale=1.0, minimum-scale=1.0, maximum-scale=2.0, user-scalable=yes" />

			<title>{% dev_name %} server</title>
			<style>
				html { font-family: Arial; display: inline-block; text-align: center; }
				h2 { font-size: 1.8rem; }
				p { font-size: 1.1rem; }
				body { max-width: 300px; margin:100px auto; padding-bottom: 25px; font-size: 0.8rem; }
				input[type="range"] { -webkit-appearance: none; appearance: none; cursor: pointer; outline: none; height: 14px; width: 50%; background: #E0E0E0; border-radius: 10px; border: solid 3px #C0C0C0; }
				input[type="range"]::-webkit-slider-thumb { -webkit-appearance: none; background: #707070; width: 24px; height: 24px; border-radius: 50%; box-shadow: 0px 3px 6px 0px rgba(0, 0, 0, 0.15); }
				input[type="range"]:active::-webkit-slider-thumb { box-shadow: 0px 5px 10px -2px rgba(0, 0, 0, 0.3); }
				input[type="text"] { width: 2em; height: 1em; font-size: 100%; }
			</style>
		</head>
		<body>
		
			<h2>{% dev_name %} server</h2>
			{% sliders %}
			
			<!--
			<span id="textSliderValue">%%SLIDERVALUE%%</span>
			-->
			
			<script>
			
			timeoutId	= null;
			function updateSliderPWM( element, moving, idx ) {
			
				if ( moving )
				{
					//	thinning out events		//	https://lab.syncer.jp/Web/JavaScript/Snippet/43/
					if ( timeoutId ) return ;
					timeoutId = setTimeout( function () { timeoutId = 0; }, 50 );
				}

				var sliderValue = document.getElementById( "pwmSlider" + idx ).value;
				document.getElementById( "valField" + idx ).value = ('00' + Number( sliderValue ).toString( 16 )).slice( -2 )
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
					value = document.getElementById( "pwmSlider" + idx ).value;
				}
				value	= (value < 0  ) ?   0 : value
				value	= (255 < value) ? 255 : value
				valueFieldElement.value = ('00' + Number( value ).toString( 16 )).slice( -2 )

				//if ( no_submit )
				//	return;

				document.getElementById( "pwmSlider" + idx ).value = value;
				console.log( value );
				var xhr = new XMLHttpRequest();
				xhr.open("GET", "/slider?value=" + value + "&idx=" + idx, true);
				xhr.send();
			}
			
			</script>

			<!--
			<form method="submit">
				ch offset:
				<select name="cch">
					{% ch-offset %}
				</select>
				<input type="submit" value="OK">
			</form><br/>
			-->

			HTTP server on <br>{% mcu %}<br/><br/>

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

	page_data[ "sliders"   ]	= get_slider_html( count, separator, 0, iref )

	for key, value in page_data.items():
		html = html.replace('{% ' + key + ' %}', value)
	
	return html

def get_slider_html( count, separator, offset, iref ):
	c	= [ "#FF0000", "#00FF00", "#0000FF", "#000000" ]
	cs	= [ "item_R", "item_G", "item_B", "item_K" ]
	s	= []

	for x in range( count ):
		i	= x + offset
		s	+= [ '<p><font color={}>PWM{}: <input type="range" oninput="updateSliderPWM( this, 1, {} )" onchange="updateSliderPWM( this, 0, {} )" id="pwmSlider{}" min="0" max="255" step="1" value="0" class="slider">'.format( c[ i % separator ], i, i, i, i ) ]
		s	+= [ '<input type="text" onchange="updateValField( this, {} )" id="valField{}" minlength=2 size=2 value="00" class="{}"></font></p>'.format( i, i, cs[ i % separator ] ) ]
		if (i + 1) % separator is 0:
			s	+= [ "<hr/>" ]
		
	if iref:
		s	+= [ '<p><font color=#000000>IREFALL:</font> <input type="range" oninput="updateSliderPWM( this,99 )" id="pwmSlider99" min="0" max="255" step="1" value="16" class="slider">' ]
		s	+= [ '<input type="text" onchange="updateValField( this, 99 )" id="valField99" minlength=2 size=2 value="00" class="item_K"></font></p>' ]

	return "\n".join( s )

main()
