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

from	nxp_periph	import	PCT2075

try:
    import usocket as socket
except:
    import socket


def start_network( port = 0, ifcnfg_param = "dhcp" ):
	print( "starting network" )

	lan = network.LAN( port )
	lan.active( True )

	print( "ethernet port {} is activated".format( port ) )

	lan.ifconfig( ifcnfg_param )
	return lan.ifconfig()

TABLE_LENGTH	= 10
SAMPLE_LENGTH	= 10
	

#Setup temp sensor
i2c	= machine.I2C( 0, freq = (400 * 1000) )
ts	= PCT2075( i2c )
rtc = machine.RTC()

data	= { "time": [], "temp": [] }

def tim_cb( tim_obj ):
	tm	= rtc.now()
	tp	= ts.temp
	data[ "time" ]	+= [ "%02d:%02d:%02d" % (tm[3], tm[4], tm[5]) ]
	data[ "temp" ]	+= [ tp ]

	over	= len( data[ "time" ] ) - SAMPLE_LENGTH
	if  0 < over:
		data[ "time" ]	= data[ "time" ][ over : ]
		data[ "temp" ]	= data[ "temp" ][ over : ]

	print( "sampled: {} @ {}".format( tp, tm ) )

def main( micropython_optimize=False ):
	
	ip_info	= start_network()

	s = socket.socket()

	ai = socket.getaddrinfo("0.0.0.0", 8080)
	addr = ai[0][-1]

	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.bind(addr)
	s.listen(5)

	tim0 = machine.Timer(0)
	tim0.init( period= 1000, callback = tim_cb)

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
		
		if ts.__class__.__name__ in req:
			print(  "new data request!" )
			html	= sending_data( data )
		else:
			html	= page_setup( ts )

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

def page_setup( dev ):
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
		<div class="header">
			<p>{% dev_name %} server</p>
			<p class="info">{% dev_info %}</p>
		</div>
		
		<div>
		<canvas id="myLineChart"></canvas>


		<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.7.2/Chart.bundle.js"></script>
		
		<script>
			var time	= []
			var temp	= []

			function drawChart( time, temp ) {
				console.log( 'drawing' );

				var ctx = document.getElementById("myLineChart");
				window.myLineChart = new Chart(ctx, {
					type: 'line',
					data: {
						labels: time,
						datasets: [
							{
								label: 'temperature',
								data: temp,
								borderColor: "rgba(255,0,0,1)",
								backgroundColor: "rgba(0,0,0,0)"
							},
							{
								label: 'sample2',
								data: [],
								borderColor: "rgba(0,0,255,1)",
								backgroundColor: "rgba(0,0,0,0)"
							},
							{
								label: 'test',
								data: [],
								borderColor: "rgba(0,255,0,1)",
								backgroundColor: "rgba(0,0,0,0)"
							},
						],
					},
					options: {
						animation: false,
						title: {
							display: true,
							text: 'temperature now'
						},
						scales: {
							yAxes: [{
								ticks: {
									suggestedMax: 30,
									suggestedMin: 20,
									stepSize: 1,
									callback: function(value, index, values){
									return  value +  ' ??C'
									}
								},
								scaleLabel: {
									display: true,
									labelString: 'temperature [??C]'
								}
							}],
							xAxes: [{
								scaleLabel: {
									display: true,
									labelString: 'time'
								}
							}]
						},
					}
				});
			}
			
			drawChart( time, temp );
			
			function doReload() {
				window.location.reload();
			}


			/****************************
			 ****	temp display
			 ****************************/

			/******** getTempAndShow ********/

			function getTempAndShow() {
				var url	= "/{% dev_name %}?"
				ajaxUpdate( url, getTempAndShowDone )
			}

			var prev_reg	= [];
			
			function getTempAndShowDone() {
				var obj = JSON.parse( this.responseText )

				//	server sends multiple data.
				//	pick one sample from last and store local memory
				time.push( obj.data.time[ obj.data.time.length - 1 ] );
				temp.push( obj.data.temp[ obj.data.time.length - 1 ] );

				drawChart( time, temp );
				
				for ( let i = 0; i < {% table_len %}; i++ )
				{
					document.getElementById( "timeField" + i ).value = time.slice( -{% table_len %} )[ {% table_len %} - i - 1 ];
					document.getElementById( "tempField" + i ).value = temp.slice( -{% table_len %} )[ {% table_len %} - i - 1 ];
				}
				
				document.getElementById( "infoFieldValue0" ).value = time[ 0 ];
				document.getElementById( "infoFieldValue1" ).value = time[ time.length - 1 ];
				document.getElementById( "infoFieldValue2" ).value = time.length;
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
				setInterval( getTempAndShow, 1000 );
			});
			
			function csvFileOut(  time, temp  ) {
				console.log( 'csvFileOut' );
				var str	= [];
				var	len	= time.length;
				
				for ( let i = 0; i < len; i++ ) {
					str	+= time[ i ] + "," +  temp[ i ] + ",\\n";
				}
				
				var blob	= new Blob( [str], {type:"text/csv"} );
				var link	= document.createElement( 'a' );
				link.href	= URL.createObjectURL( blob );
				link.download	= "{% dev_name %}_measurement_result.csv";
				link.click();
			}
		</script>

		</div>
		
		<div class="para">
			<div id="reg_table" class="control_panel reg_table log_panel">
					{% table %}
			</div>
			<div id="reg_table" class="control_panel reg_table info_panel">
				{% info_tab %}<br/>
				<input type="button" onclick="csvFileOut( time, temp );" value="Save" class="save">
			</div>
		</div>

	</body>
	</html>
	"""
	page_data	= {}
	page_data[ "dev_name"  ]	= dev.__class__.__name__
	page_data[ "dev_info"  ]	= dev.info()
	page_data[ "table"     ]	= get_table( TABLE_LENGTH )
	page_data[ "info_tab"  ]	= get_info_table( 3 )
	page_data[ "table_len" ]	= str( TABLE_LENGTH )
	page_data[ "style"     ]	= get_style()

	for key, value in page_data.items():
		html = html.replace('{% ' + key + ' %}', value )
	
	return html

def get_table( max ):
	s	= [ '<table><tr><td>time</td><td>temp [??C]</td></tr>' ]

	for i in range( max ):
		s	+= [ '<tr><td text_align="center"><input type="text" id="timeField{}" value = "---"></td><td><input type="text" id="tempField{}"></td></tr>'.format( i, i ) ]

	s	+= [ '</table>' ]

	return "\n".join( s )

def get_info_table( length ):
	lb	= [ "start time", "last time", "sample count" ]
	s	= [ '<table><tr>' ]

	for i, l in zip( range( length ), lb ):
		s	+= [ '<tr><td text_align="center">{}</td><td><input type="text" id="infoFieldValue{}"></td></tr>'.format( l, i ) ]

	s	+= [ '</table>' ]

	return "\n".join( s )


def sending_data( data ):
	s	 = [ 'HTTP/1.0 200 OK\n\n' ]
	s	+= [ ujson.dumps( { "data": data } ) ]

	return "".join( s )

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
		/* width: 2em; */
		height: 1em;
		font-size: 100%;
		text-align: center;
		border: solid 0px #FFFFFF;
	}
	table {
		background-color: #FFFFFF;
		border-collapse: collapse;
	}
	td {
		border: solid 1px #EEEEEE;
		text-align: center;
	}
	
	.para {
		display: flex;
	}

	.log_panel, .info_panel {
		border: solid 0px #FFFFFF;
		padding: 5px;
	}

	
	</style>
	"""
	return s

main()
