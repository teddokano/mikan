#	MicroPython HTTP server sample code based on "http_server_simplistic.py".
#	https://github.com/micropython/micropython/blob/master/examples/network/http_server_simplistic.py
#
#	Tedd OKANO / Released under the MIT license
#	18-Oct-2022
#	version	0.1

import	network
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


#Setup temp sensor
i2c	= machine.I2C( 0, freq = (400 * 1000) )
ts	= PCT2075( i2c )
rtc = machine.RTC()


def main( micropython_optimize=False ):
	time	= []
	temp	= []
	
	ip_info	= start_network()

	s = socket.socket()

	ai = socket.getaddrinfo("0.0.0.0", 8080)
	print("Bind address info:", ai)
	addr = ai[0][-1]

	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.bind(addr)
	s.listen(5)
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
		
		if "/?LED=ON0" in req:
			led0.v	= 1.0

		while True:
			h = client_stream.readline()
			if h == b"" or h == b"\r\n":
				break
			#print(h)
		
		t		= rtc.now()
		time	+= [ "%02d:%02d:%02d" % (t[3], t[4], t[5]) ]
		temp	+= [ ts.temp ]
		html	= page_setup( ts, time, temp )

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
			input[type="text"] { width: 2em; height: 1em; font-size: 100%; }
			table { background-color: #EEEEEE; border-collapse: collapse; width: 30%; }
			td { border: solid 1px; color: #000000; }
		</style>
	</head>
	<body>
		<h1>{% dev_name %} server</h1>
		<canvas id="myLineChart"></canvas>
		<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.7.2/Chart.bundle.js"></script>
		
		<script>
			var ctx = document.getElementById("myLineChart");
			var myLineChart = new Chart(ctx, {
				type: 'line',
				data: {
					labels: {% time %},
					datasets: [
						{
							label: 'temperature',
							data: {% temp %},
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
								return  value +  ' ˚C'
								}
							},
							scaleLabel: {
								display: true,
								labelString: 'temperature [˚C]'
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
			
			function doReload() {
				window.location.reload();
			}
			 
			window.addEventListener('load', function () {
				setTimeout(doReload, 1000);}
			);

		</script>
		
		{% table %}	<br/>

	</body>
	</html>
	"""
	
	page_data	= {}
	page_data[ "dev_name" ]	= dev.__class__.__name__
	page_data[ "time"  ]	= str( time )
	page_data[ "temp"  ]	= str( temp )
	page_data[ "table" ]	= get_table( time, temp, max )

	for key, value in page_data.items():
		html = html.replace('{% ' + key + ' %}', value )
	
	return html

def get_table( time, temp, max ):
	s	= [ '<table><tr><td>time</td><td>temp [˚C]</td><tr>' ]
	
	for i, j in zip( time[-5:], temp[-5:] ):
		s	+= [ '<tr><td>{}</td><td>{}</td></tr>'.format( i, j ) ]
	
	s	+= [ '</table>' ]
	
	return "\n".join( s )

main()
