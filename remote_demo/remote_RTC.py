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

from	nxp_periph	import	PCF2131

try:
    import usocket as socket
except:
    import socket

WKDY	= ( "Sunday", "Monday", "Tuesday", "Wednesday",
			"Thursday", "Friday", "Saturday" )
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

TABLE_LENGTH	= 10
	
#Setup RTC
i2c	= machine.I2C( 0, freq = (400 * 1000) )
rtc	= PCF2131( i2c )
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
		
		td		= rtc.__get_datetime_reg()

		if "newdata.html" in req:
			print(  "new data request!" )
			html	= sending_data( td )
		else:
			html	= page_setup( rtc, time, temp )

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
		<title>temp sensor</title>
		<style>
			html { font-family: Arial; display: inline-block; text-align: center; }
			h2 { font-size: 1.8rem; }
			p { font-size: 1.1rem; }
			body { margin:100px auto; padding: 5px; font-size: 0.8rem; }
			input[type="range"] { -webkit-appearance: none; appearance: none; cursor: pointer; outline: none; height: 5px; width: 80%; background: #E0E0E0; border-radius: 10px; border: solid 3px #C0C0C0; }
			input[type="range"]::-webkit-slider-thumb { -webkit-appearance: none; background: #707070; width: 20px; height: 20px; border-radius: 50%; box-shadow: 0px 3px 6px 0px rgba(0, 0, 0, 0.15); }
			input[type="range"]:active::-webkit-slider-thumb { box-shadow: 0px 5px 10px -2px rgba(0, 0, 0, 0.3); }
			input[type="text"] { width: 8em; height: 1em; font-size: 100%; border: solid 0px; }
			table { background-color: #FFFFFF; border-collapse: collapse; width: 30%; }
			td { border: solid 1px; color: #000000; }
			.datetime { font-size: 3.0rem; }
		</style>
	</head>
	<body>
		<h1>{% dev_name %} server</h1>		
		<script>
			function ajaxUpdate( url, element ) {
				url			= url + '?ver=' + new Date().getTime();
				var ajax	= new XMLHttpRequest;
				ajax.open( 'GET', url, true );
				
				ajax.onload = function () {
					var obj = JSON.parse( ajax.responseText )
					console.log( obj.datetime.str );

					var elem = document.getElementById( "datetime" );
					elem.innerText = obj.datetime.str;
				};

				ajax.send( null );
			}

			window.addEventListener('load', function () {
				console.log( 'window.addEventListener' );

				var url = "newdata.html";
				var div = document.getElementById('ajaxreload');
				setInterval( function () {
				ajaxUpdate( url, div );
				}, 1000);
			});

			</script>			
			<div id="datetime" class="datetime"></div>
	
	</body>
	</html>
	"""
	page_data	= {}
	page_data[ "dev_name" ]	= dev.__class__.__name__

	for key, value in page_data.items():
		html = html.replace('{% ' + key + ' %}', value )
	
	return html

def sending_data( td ):
	td[ "weekday" ]	= WKDY[ td[ "weekday" ] ]
	td[ "month"   ]	= MNTH[ td[ "month"   ] ]
	td[ "str"   ]	 = "%04d %s %02d (%s) %02d:%02d:%02d" % \
						(td[ "year" ], td[ "month" ], td[ "day" ], td[ "weekday" ], \
						td[ "hours" ], td[ "minutes" ], td[ "seconds" ] )
	s	 = 'HTTP/1.0 200 OK\n\n' + ujson.dumps( { "datetime": td } )
	
	return s
	
main()
