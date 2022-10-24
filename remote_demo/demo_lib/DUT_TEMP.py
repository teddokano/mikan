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
from	nxp_periph	import	temp_sensor_base
import	demo_lib.util

class DUT_TEMP():
	APPLIED_TO		= temp_sensor_base
	TABLE_LENGTH	= 10
	SAMPLE_LENGTH	= 10
	GRAPH_HIGH		= 30
	GRAPH_LOW		= 20

	regex_thresh	= ure.compile( r".*tos=(\d+\.\d+)&thyst=(\d+\.\d+)" )
	regex_heater	= ure.compile( r".*heater=(\d+)" )
	regex_mode		= ure.compile( r".*os_polarity=(\d+)&os_mode=(\d+)" )

	def __init__( self, dev, timer = 0, sampling_interbal = 1.0 ):
		self.interface	= dev.__if
		self.dev		= dev
		self.type		= self.dev.__class__.__name__
		self.address	= dev.__adr
		self.dev_name	= self.type + "_on_I2C(0x%02X)" % (dev.__adr << 1)
		self.data		= { "time": [], "temp": [], "tos": [], "thyst": [], "os": [], "heater": [] }
		self.rtc		= machine.RTC()	#	for timestamping on samples
		self.info		= [ "temp sensor", "" ]

		tp	= self.dev.temp

		self.tos		= int( (tp + 2) * 2 ) / 2
		self.thyst		= int( (tp + 1) * 2 ) / 2

		self.dev.temp_setting( [ self.tos, self.thyst ] )

		self.int_pin		= machine.Pin( "D2", machine.Pin.IN  )
		self.heater_pin		= machine.Pin( "D3", machine.Pin.OUT )	#	R19 as heater
		self.heater( 0 )

		self.dev.ping()
		if self.dev.live:
			tim0	= machine.Timer( timer )
			tim0.init( period = int( sampling_interbal * 1000.0 ), callback = self.tim_cb )

	def heater( self, *args ):
		if args:
			self.heater_state	= args[ 0 ]
			self.heater_pin.value( self.heater_state )
			print( "------------------------------ heater setting:%d" % self.heater_state )
		else:
			print( "------------------------------ heater setting read:%d" % self.heater_state )
			return self.heater_state

	def tim_cb( self, tim_obj ):
		tp	= self.dev.temp
		tm	= self.rtc.now()
		self.data[ "time"   ]	+= [ "%02d:%02d:%02d" % (tm[3], tm[4], tm[5]) ]
		self.data[ "temp"   ]	+= [ tp ]
		self.data[ "tos"    ]	+= [ self.tos ]
		self.data[ "thyst"  ]	+= [ self.thyst ]
		self.data[ "os"     ]	+= [ self.GRAPH_HIGH if self.int_pin.value() else self.GRAPH_LOW ]
		self.data[ "heater" ]	+= [ self.GRAPH_HIGH if self.heater()        else self.GRAPH_LOW ]

		over	= len( self.data[ "time" ] ) - self.SAMPLE_LENGTH
		if  0 < over:
			self.data[ "time"   ]	= self.data[ "time"   ][ over : ]
			self.data[ "temp"   ]	= self.data[ "temp"   ][ over : ]
			self.data[ "tos"    ]	= self.data[ "tos"    ][ over : ]
			self.data[ "thyst"  ]	= self.data[ "thyst"  ][ over : ]
			self.data[ "os"     ]	= self.data[ "os"     ][ over : ]
			self.data[ "heater" ]	= self.data[ "heater" ][ over : ]

		#print( "sampled: {} @ {}".format( tp, tm ) )

	def parse( self, req ):
		if self.dev_name not in req:
			return None

		if "?" not in req:
			html	= self.page_setup()
		elif "update" in req:
				html	= self.sending_data()
		else:
			print( req )
			html	= 'HTTP/1.0 200 OK\n\n'	# dummy

			m	= self.regex_thresh.match( req )
			if m:
				self.tos	= float( m.group( 1 ) )
				self.thyst	= float( m.group( 2 ) )
				self.dev.temp_setting( [ self.tos, self.thyst ] )
				print( "********** THRESHOLDS {} {} **********".format( self.tos, self.thyst ) )

			m	= self.regex_heater.match( req )
			if m:
				val	= int( m.group( 1 ) )
				self.heater( val )
				print( "********** {} HEATER {} **********".format( self.type, "ON" if val else "OFF" ) )

			m	= self.regex_mode.match( req )
			if m:
				pol	= int( m.group( 1 ) )
				mod	= int( m.group( 2 ) )
				self.dev.bit_operation( "Conf", 0x06, (pol << 2) | (mod << 1) )

				print( "********** CONFIGURATION {} {} **********".format( "Active_HIGH" if pol else "Active_Low", "Interrupt" if mod else "Comparator" ) )

		return html

	def sending_data( self ):
		s	 = [ 'HTTP/1.0 200 OK\n\n' ]
		s	+= [ ujson.dumps( { "data": self.data } ) ]

		return "".join( s )

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
			<div id="temperature" class="datetime"></div>

			<div>
			<canvas id="myLineChart"></canvas>
			<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.7.2/Chart.bundle.js"></script>
			
			<script>
				const	TABLE_LEN	= {% table_len %}
				const	DEV_NAME	= '{% dev_name %}';
				const	GRAPH_HIGH	= {% graph_high %}
				const	GRAPH_LOW	= {% graph_low %}
				const	TOS_INIT	= {% tos_init %}
				const	THYST_INIT	= {% thyst_init %}
				const	REQ_HEADER	= '/' + DEV_NAME + '?';
				const	OS_LABEL	= 'OS pin ( high@' + GRAPH_HIGH + ' / low@' + GRAPH_LOW + ' )'

				let	time	= []
				let	temp	= []
				let	tos		= []
				let	thyst	= []
				let	os		= []
				let	heater	= []

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
									borderColor: "rgba( 255, 0, 0, 1 )",
									backgroundColor: "rgba( 0, 0, 0, 0 )"
								},
								{
									label: 'Tos',
									data: tos,
									borderColor: "rgba( 255, 0, 0, 0.3 )",
									backgroundColor: "rgba( 0, 0, 0, 0 )"
								},
								{
									label: 'Thyst',
									data: thyst,
									borderColor: "rgba( 0, 0, 255, 0.3 )",
									backgroundColor: "rgba( 0, 0, 0, 0 )"
								},
								{
									label: OS_LABEL,
									data: os,
									borderColor: "rgba( 0, 255, 0, 0.5 )",
									backgroundColor: "rgba( 0, 0, 0, 0 )"
								},
								{
									label: 'Heater',
									data: heater,
									borderColor: "rgba( 255, 0, 0, 0.0 )",
									backgroundColor: "rgba( 255, 0, 0, 0.1 )"
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
										suggestedMax: GRAPH_HIGH,
										suggestedMin: GRAPH_LOW,
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
				
				/****************************
				 ****	temp display
				 ****************************/

				/******** getTempAndShow ********/

				function getTempAndShow() {
					let url	= REQ_HEADER + "update";
					ajaxUpdate( url, getTempAndShowDone );
				}

				let prev_reg	= [];
				
				function getTempAndShowDone() {
					let obj = JSON.parse( this.responseText );

					//	server sends multiple data.
					//	pick one sample from last and store local memory
					idx	= obj.data.time.length - 1;
					temperature	= obj.data.temp[ idx ];
					
					time.push( obj.data.time[ idx ] );
					temp.push( temperature );
					tos.push( obj.data.tos[ idx ] );
					thyst.push( obj.data.thyst[ idx ] );
					os.push( obj.data.os[ idx ] );
					heater.push( obj.data.heater[ idx ] );

					drawChart( time, temp );
					
					var elem = document.getElementById( "temperature" );
					elem.innerText = temperature.toFixed( 3 ) + '˚C';

					
					for ( let i = 0; i < TABLE_LEN; i++ )
					{
						document.getElementById( "timeField" + i ).value = time.slice( -{% table_len %} )[ {% table_len %} - i - 1 ];
						
						let	value	= temp.slice( -{% table_len %} )[ {% table_len %} - i - 1 ];
						
						if ( !isNaN( value ) )
							value	= value.toFixed( 3 );
							
						document.getElementById( "tempField" + i ).value = value;
					}
					
					document.getElementById( "infoFieldValue0" ).value = time[ 0 ];
					document.getElementById( "infoFieldValue1" ).value = time[ time.length - 1 ];
					document.getElementById( "infoFieldValue2" ).value = time.length;
				}

				function doReload() {
					window.location.reload();
				}

				/****************************
				 ****	widget handling
				 ****************************/
				
				let timeoutId	= null;

				/******** updateSlider ********/

				function updateSlider( element, moving, idx ) {
					let tos		= document.getElementById( "Slider0" ).value;
					let thyst	= document.getElementById( "Slider1" ).value;

					tos		= parseFloat( tos );	//	<-- this is required to let correct compare
					thyst	= parseFloat( thyst );	//	<-- this is required to let correct compare

					if ( idx == 0 ) {
						thyst	= ( tos < thyst ) ? tos : thyst;
						//thyst=tos;
					}
					else {
						tos		= ( tos < thyst ) ? thyst : tos;
						//tos=thyst;
					}

					setSliderValues( 0, tos   );
					setSliderValues( 1, thyst );
				}
				
				/******** updateValField ********/

				function updateValField( element, idx ) {
					let valueFieldElement = document.getElementById( "valField" + idx );
					let value	= parseFloat( valueFieldElement.value );
					let no_submit	= 0;
					
					if ( isNaN( value ) ) {
						no_submit	= 1;
						value = document.getElementById( "Slider" + idx ).value;
					}
					value	= (value < -55  ) ? -55 : value;
					value	= (125   < value) ? 125 : value;

					setSliderValues( idx, value );
				}
				
				/******** setSliderValues ********/

				function setSliderValues( idx, value ) {

					document.getElementById( "Slider" + idx ).value = value;
					document.getElementById( "valField" + idx ).value = value.toFixed( 1 );
				}

				/******** setTosThyst ********/

				function setTosThyst() {
					let valueFieldElementTos	= document.getElementById( "valField0" );
					let valueFieldElementThyst	= document.getElementById( "valField1" );
					let tos		= parseFloat( valueFieldElementTos.value );
					let thyst	= parseFloat( valueFieldElementThyst.value );

					let url	= REQ_HEADER + 'tos=' + tos.toFixed( 1 ) + '&thyst=' + thyst.toFixed( 1 );
					ajaxUpdate( url, setTosThystDone );
				}
				
				/******** setTosThystDone ********/

				function setTosThystDone() {
					let obj = JSON.parse( this.responseText );
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
					return ('00' + Number( num ).toString( 16 ).toUpperCase()).slice( -2 );
				}


				window.addEventListener('load', function () {
					console.log( 'window.addEventListener' );
					setInterval( getTempAndShow, 1000 );
				});
				
				function csvFileOut(  time, temp  ) {
					console.log( 'csvFileOut' );
					let str	= [];
					let	len	= time.length;
					
					str	+= "time,temp,tos,thyst,os\\n";
					for ( let i = 0; i < len; i++ ) {
						str	+= time[ i ] + "," +  temp[ i ] + "," + tos[ i ] + "," + thyst[ i ] + "," + os[ i ] + "\\n";
					}
					
					let blob	= new Blob( [str], {type:"text/csv"} );
					let link	= document.createElement( 'a' );
					link.href	= URL.createObjectURL( blob );
					link.download	= DEV_NAME + "_measurement_result.csv";
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
					<input type="button" onclick="csvFileOut( time, temp );" value="Save" class="tmp_button">
				</div>
				
				<div id="reg_table" class="control_panel reg_table info_panel">
					<table class="table_TEMP_slider">
						<tr class="slider_table_row">
							<td class="td_TEMP_slider" text_align="center">
								Tos
							</td>
							<td class="td_TEMP_slider" text_align="center">
								<input type="range" oninput="updateSlider( this, 1, 0 )" onchange="updateSlider( this, 0, 0 )" id="Slider0" min="-55" max="125" step="0.5" value="{% tos_init %}" class="slider">
							</td>
							<td class="td_TEMP_slider" text_align="center">
								<input type="text" onchange="updateValField( this, 0 )" id="valField0" minlength=4 size=5 value="{% tos_init %}""><br/>
								
							</td>
						</tr>
						<tr class="slider_table_row">
							<td class="td_TEMP_slider" text_align="center">
								Thyst
							</td>
							<td class="td_TEMP_slider">
								<input type="range" oninput="updateSlider( this, 1, 1 )" onchange="updateSlider( this, 0, 1 )" id="Slider1" min="-55" max="125" step="0.5" value="{% thyst_init %}" class="slider">
							</td>
							<td class="td_TEMP_slider">
								<input type="text" onchange="updateValField( this, 1 )" id="valField1" minlength=4 size=5 value="{% thyst_init %}">
							</td>
						</tr>
					</table>
					<input type="button" onclick="setTosThyst();" value="Update Tos&Thys" class="tmp_button"><br/>

					<hr/>

					<form id="config_panel" class="control_panel reg_table log_panel"">
						<table class="table_TEMP"><tr>
							<td class="td_TEMP_la">OS polarity</td>
							<td class="td_TEMP_la">
								<input type="radio" name="os_polarity" id="active_low"  value="0" checked="checked"><label for="active_low">Active LOW<label><br>
								<input type="radio" name="os_polarity" id="active_high" value="1"><label for="active_high">Active HIGH<label><br/>
						</td></tr>
						<tr>
							<td class="td_TEMP_la">OS operation mode</td>
							<td class="td_TEMP_la">
								<input type="radio" name="os_mode" id="comparator" value="0" checked="checked"><label for="comparator">Comparator<label><br>
								<input type="radio" name="os_mode" id="interrupt"  value="1"><label for="interrupt" >Interrupt <label>
							</td>
						</tr></table>
					</form>
					<input type="button" onclick="setConfig();" value="Set" class="tmp_button"><br/>

					<script>
						function setConfig() {
							let config_panel = document.getElementById( 'config_panel' );
							radioNodeList = config_panel.elements[ 'os_polarity' ];
							let	pol	= radioNodeList.value;
							radioNodeList = config_panel.elements[ 'os_mode' ];
							let	mod	= radioNodeList.value;
							
							let url	= REQ_HEADER + 'os_polarity=' + pol + '&os_mode=' + mod;
							ajaxUpdate( url );
						}
					</script>

					<hr/>

					<input type="checkbox" onchange="updateHeaterSwitch( this );" id="heaterSwitch">
					<label for="heaterSwitch">heater</label>
	
	
					<script>
						function updateHeaterSwitch( element ) {
							let heaterSwitchElement	= document.getElementById( "heaterSwitch" );
							let	val;
							
							if ( heaterSwitchElement.checked )
								val	= 1;
							else
								val	= 0;
								
							let url	= REQ_HEADER + 'heater=' + val;
							ajaxUpdate( url );
						}
					</script>



				</div>

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
		page_data[ "dev_type"  ]	= self.type
		page_data[ "dev_info"  ]	= self.dev.info()
		page_data[ "table_len" ]	= str( self.TABLE_LENGTH )
		page_data[ "mcu"       ]	= os.uname().machine
		page_data[ "table"     ]	= self.get_table()
		page_data[ "info_tab"  ]	= self.get_info_table()
		page_data[ "style"     ]	= demo_lib.util.get_css()

		page_data[ "graph_high"]	= str( self.GRAPH_HIGH )
		page_data[ "graph_low" ]	= str( self.GRAPH_LOW  )
		page_data[ "tos_init"  ]	= str( self.tos   )
		page_data[ "thyst_init"]	= str( self.thyst )

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
