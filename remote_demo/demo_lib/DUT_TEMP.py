#	MicroPython HTTP server sample code based on "http_server_simplistic.py".
#	https://github.com/micropython/micropython/blob/master/examples/network/http_server_simplistic.py
#
#	Tedd OKANO / Released under the MIT license
#	22-Oct-2022
#	version	0.1
#
# https://www.sejuku.net/blog/25316
# https://micropython-docs-ja.readthedocs.io/ja/v1.10ja/library/ujson.html
# https://qiita.com/otsukayuhi/items/31ee9a761ce3b978c87a
# https://products.sint.co.jp/topsic/blog/json
# https://rintama.net/%EF%BD%8A%EF%BD%81%EF%BD%96%EF%BD%81%EF%BD%93%EF%BD%83%EF%BD%92%EF%BD%89%EF%BD%90%EF%BD%94%E3%81%A7%E4%BD%9C%E6%88%90%E3%81%97%E3%81%9F%E9%85%8D%E5%88%97%E3%82%92%EF%BD%83%EF%BD%93%EF%BD%96%E3%81%A7/

import	machine
import	os
import	ure
import	ujson

from	nxp_periph	import	PCT2075, LM75B
import	demo_lib.util

class DUT_TEMP():
	TABLE_LENGTH	= 10
	SAMPLE_LENGTH	= 10
		
	def __init__( self, dev, timer = 0, sampling_interbal = 1.0 ):
		self.interface	= dev.__if
		self.dev		= dev
		self.type		= self.dev.__class__.__name__
		self.address	= dev.__adr
		self.dev_name	= self.type + "_on_I2C(0x%02X)" % (dev.__adr << 1)
		self.data		= { "time": [], "temp": [] }
		self.rtc		= machine.RTC()	#	for timestamping on samples
		self.info		= [ "temp sensor", "" ]

		self.dev.ping()
		if self.dev.live:
			tim0	= machine.Timer( timer )
			tim0.init( period = int( sampling_interbal * 1000.0 ), callback = self.tim_cb )

	def tim_cb( self, tim_obj ):
		tp	= self.dev.temp
		tm	= self.rtc.now()
		self.data[ "time" ]	+= [ "%02d:%02d:%02d" % (tm[3], tm[4], tm[5]) ]
		self.data[ "temp" ]	+= [ tp ]

		over	= len( self.data[ "time" ] ) - self.SAMPLE_LENGTH
		if  0 < over:
			self.data[ "time" ]	= self.data[ "time" ][ over : ]
			self.data[ "temp" ]	= self.data[ "temp" ][ over : ]

		#print( "sampled: {} @ {}".format( tp, tm ) )

	def parse( self, req ):
		if self.dev_name not in req:
			return None

		if "?" not in req:
			html	= self.page_setup()
		else:
			print(  "new data request!" )
			html	= self.sending_data()

		return html

	def page_setup( self ):
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
				<p>{% dev_type %} server</p>
				<p class="info">{% dev_info %}</p>
			</div>
			
			<div>
			<canvas id="myLineChart"></canvas>
			<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.7.2/Chart.bundle.js"></script>
			
			<script>
				const	TABLE_LEN = {% table_len %}
				let		time	= []
				let		temp	= []

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
					let url	= "/{% dev_name %}?"
					ajaxUpdate( url, getTempAndShowDone )
				}

				let prev_reg	= [];
				
				function getTempAndShowDone() {
					let obj = JSON.parse( this.responseText )

					//	server sends multiple data.
					//	pick one sample from last and store local memory
					time.push( obj.data.time[ obj.data.time.length - 1 ] );
					temp.push( obj.data.temp[ obj.data.time.length - 1 ] );

					drawChart( time, temp );
					
					for ( let i = 0; i < TABLE_LEN; i++ )
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
					let	ajax	= new XMLHttpRequest;
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
					let str	= [];
					let	len	= time.length;
					
					for ( let i = 0; i < len; i++ ) {
						str	+= time[ i ] + "," +  temp[ i ] + ",\\n";
					}
					
					let blob	= new Blob( [str], {type:"text/csv"} );
					let link	= document.createElement( 'a' );
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

				<div class="foot_note">
					<b>HTTP server on<br/>
					{% mcu %}</b><br/>
					0100111101101011011000010110111001101111
				</div>
			</div>

		</body>
		</html>
		"""
		page_data	= {}
		page_data[ "dev_name"  ]	= self.dev_name
		page_data[ "dev_type"  ]	= self.type
		page_data[ "dev_info"  ]	= self.dev.info()
		page_data[ "table_len" ]	= str( self.TABLE_LENGTH )
		page_data[ "mcu"       ]	= os.uname().machine
		page_data[ "table"     ]	= self.get_table()
		page_data[ "info_tab"  ]	= self.get_info_table()
		page_data[ "style"     ]	= demo_lib.util.get_css()

		for key, value in page_data.items():
			html = html.replace('{% ' + key + ' %}', value )
		
		return html

	def get_table( self ):
		s	= [ '<table class="table_TEMP"><tr><td class="td_TEMP">time</td><td class="td_TEMP">temp [˚C]</td></tr>' ]

		for i in range( self.TABLE_LENGTH ):
			s	+= [ '<tr><td class="td_TEMP" text_align="center"><input class="input_text_TMP" type="text" id="timeField{}" value = "---"></td><td class="td_TEMP"><input class="input_text_TMP" type="text" id="tempField{}"></td></tr>'.format( i, i ) ]

		s	+= [ '</table>' ]

		return "\n".join( s )

	def get_info_table( self ):
		lb	= [ "start time", "last time", "sample count" ]
		s	= [ '<table class="table_TEMP"><tr>' ]

		for i, l in zip( range( len( lb ) ), lb ):
			s	+= [ '<tr><td class="td_TEMP" text_align="center">{}</td><td class="td_TEMP"><input class="input_text_TMP" type="text" id="infoFieldValue{}"></td></tr>'.format( l, i ) ]

		s	+= [ '</table>' ]

		return "\n".join( s )


	def sending_data( self ):
		s	 = [ 'HTTP/1.0 200 OK\n\n' ]
		s	+= [ ujson.dumps( { "data": self.data } ) ]

		return "".join( s )
