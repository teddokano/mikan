#	MicroPython HTTP server sample code based on "http_server_simplistic.py".
#	https://github.com/micropython/micropython/blob/master/examples/network/http_server_simplistic.py
#
#	Tedd OKANO / Released under the MIT license
#	18-Oct-2022
#	version	0.1
#
# https://www.sejuku.net/blog/25316
# https://micropython-docs-ja.readthedocs.io/ja/v1.10ja/library/ujson.html
# https://qiita.com/otsukayuhi/items/31ee9a761ce3b978c87a
# https://products.sint.co.jp/topsic/blog/json
# https://rintama.net/%EF%BD%8A%EF%BD%81%EF%BD%96%EF%BD%81%EF%BD%93%EF%BD%83%EF%BD%92%EF%BD%89%EF%BD%90%EF%BD%94%E3%81%A7%E4%BD%9C%E6%88%90%E3%81%97%E3%81%9F%E9%85%8D%E5%88%97%E3%82%92%EF%BD%83%EF%BD%93%EF%BD%96%E3%81%A7/

import	network
import	ujson
import	machine
import	ure

from	nxp_periph	import	PCF2131, PCF85063

try:
    import usocket as socket
except:
    import socket

WKDY	= ( "Monday", "Tuesday", "Wednesday",
			"Thursday", "Friday", "Saturday", "Sunday" )
MNTH	= ( "None", "January", "February", "March",
			"April", "May", "June", "July", "August",
			"September", "October", "Nobemver", "Decemver" )

def start_network( port = 0, ifcnfg_param = "dhcp" ):
	print( "starting network" )

	lan = network.LAN( port )
	lan.active( True )

	print( "ethernet port {} is activated".format( port ) )

	lan.ifconfig( ifcnfg_param )
	return lan.ifconfig()

regex_reg	= ure.compile( r".*reg=(\d+)&val=(\d+)" )

#Setup RTC
i2c	= machine.I2C( 0, freq = (400 * 1000) )
rtc	= PCF2131( i2c )
#rtc	= PCF85063( i2c )
mrtc = machine.RTC()

def main( micropython_optimize=False ):
	time	= []
	temp	= []
	
	ip_info	= start_network()

	s = socket.socket()

	ai = socket.getaddrinfo("0.0.0.0", 8080)
	addr = ai[0][-1]

	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.bind(addr)
	s.listen(5)
	print("Listening, connect your browser to http://{}:8080/".format( ip_info[0] ))

	SAMPLE_LENGTH	= 10
	html	= 'HTTP/1.0 200 OK\n\n'

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
			html	= page_setup( rtc, time, temp )
		else:
			
			m	= regex_reg.match( req )
			if m:
				print( m.groups() )
				reg	= int( m.group( 1 ) )
				val	= int( m.group( 2 ) )

				rtc.write_registers( reg, val )
				html	= 'HTTP/1.0 200 OK\n\n' + ujson.dumps( { "reg": reg, "val": val } )

			else:
				html	= sending_data( rtc )


		while True:
			h = client_stream.readline()
			if h == b"" or h == b"\r\n":
				break
			#print(h)

		client_stream.write( html )

		client_stream.close()
		if not micropython_optimize:
			client_sock.close()
			
		print()

def page_setup( dev, time, temp ):
	#HTML to send to browsers
	html = """\
	HTTP/1.0 200 OK

	<!--
	https://qiita.com/Haruka-Ogawa/items/59facd24f2a8bdb6d369
	-->

	<!DOCTYPE html>
	<html>
		<head>
			<meta charset="utf-8" />
			<title>{% dev_name %} server</title>
			{% style %}
		</head>
		<body>
			<script>

				/****************************
				 ****	time display
				 ****************************/
				 
				/******** getTimeAndShow ********/

				function getTimeAndShow() {
					var url	= "/{% dev_name %}?"
					ajaxUpdate( url, getTimeAndShowDone )
				}

				/******** getTimeAndShowDone ********/

				var prev_reg	= [];
				
 				function getTimeAndShowDone() {
					var obj = JSON.parse( this.responseText )
					console.log( obj.datetime.str );

					var elem = document.getElementById( "datetime" );
					elem.innerText = obj.datetime.str;
					
						for ( let i = 0; i < obj.reg.length; i++ ) {
							var value	= obj.reg[ i ];
							if ( value != prev_reg[ i ] ) {
								document.getElementById('regField' + i ).value	= hex( value );
							}
						}
						prev_reg	= obj.reg;
				}


				/****************************
				 ****	register controls
				 ****************************/
				 
				/******** updateRegField ********/

				function updateRegField( element, idx ) {
					var valueFieldElement = document.getElementById( "regField" + idx );
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

					var url	= "/{% dev_name %}?reg=" + idx + "&val=" + value
					ajaxUpdate( url, updateRegFieldDone )
				}
				
				function updateRegFieldDone() {
					obj = JSON.parse( this.responseText );
					
					document.getElementById('regField' + obj.reg ).value	= hex( obj.val )
				}


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


				window.addEventListener('load', function () {
					console.log( 'window.addEventListener' );
					setInterval( getTimeAndShow, 1000 );
				});

				</script>

				<div class="header">
					<p>{% dev_name %} server</p>
					<p class="info">{% dev_info %}</p>
				</div>

				<div id="datetime" class="datetime"></div>
				
				<div id="reg_table" class="control_panel reg_table">
					register table<br/>
					{% reg_table %}
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
	page_data[ "dev_name"   ]	= dev.__class__.__name__
	page_data[ "dev_info"  ]	= dev.info()
	page_data[ "mcu"       ]	= os.uname().machine
	page_data[ "reg_table"  ]	= get_reg_table( rtc, 4 )
	page_data[ "style"     ]	= get_style()

	for key, value in page_data.items():
		html = html.replace('{% ' + key + ' %}', value )
	
	return html

def sending_data( rtc ):
	reg	= rtc.dump()
	td	= rtc.__get_datetime_reg()
	
	td[ "weekday" ]	= WKDY[ td[ "weekday" ] ]
	td[ "month"   ]	= MNTH[ td[ "month"   ] ]
	td[ "str"   ]	 = "%04d %s %02d (%s) %02d:%02d:%02d" % \
						(td[ "year" ], td[ "month" ], td[ "day" ], td[ "weekday" ], \
						td[ "hours" ], td[ "minutes" ], td[ "seconds" ] )
	
	return 'HTTP/1.0 200 OK\n\n' + ujson.dumps( { "datetime": td, "reg": reg } )


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



def get_reg_table2( dev, cols ):
	total	= len( dev.REG_NAME )
	rows	= (total + cols - 1) // cols

	s	 	= [ '<table>' ]

	for y in range( rows ):
		s	 	+= [ '<tr>' ]
		for i in range( y, total, rows ):
			s	+= [ '<td>{}</td><td>0x{:02X}</td>'.format( dev.REG_NAME[ i ], i ) ]
			s	+= [ '<td><input type="text" onchange="updateRegField( this, {} )" id="regField{}" minlength=2 size=2 value="00" class="regfield"></td>'.format( i, i ) ]

		s	+= [ '</tr>' ]

	s	+= [ '</table>' ]
	return "\n".join( s )

def get_style():
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
	.datetime {
		font-size: 3.0rem;
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
