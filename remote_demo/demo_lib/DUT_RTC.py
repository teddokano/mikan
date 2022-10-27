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

from	nxp_periph	import	PCF2131, PCF85063
from	nxp_periph	import	RTC_base
import	demo_lib.util

try:
	import	demo_lib.sound_data as sound_data
except:
	import	demo_lib.no_sound_data as sound_data



class DUT_RTC():
	APPLIED_TO	= RTC_base
	
	WKDY	= ( "Monday", "Tuesday", "Wednesday",
				"Thursday", "Friday", "Saturday", "Sunday" )
	MNTH	= ( "None", "January", "February", "March",
				"April", "May", "June", "July", "August",
				"September", "October", "Nobemver", "Decemver" )

	DS_URL		= { "PCF2131_I2C": "https://www.nxp.com/docs/en/data-sheet/PCF2131DS.pdf",
					"PCF2131_SPI": "https://www.nxp.com/docs/en/data-sheet/PCF2131DS.pdf",
					"PCF85063": "https://www.nxp.com/docs/en/data-sheet/PCF85063A.pdf",
					}

	regex_reg	= ure.compile( r".*reg=(\d+)&val=(\d+)" )
	regex_alarm	= ure.compile( r".*alarm&weekday=(\d+)&day=(\d+)&hour=(\d+)&minute=(\d+)&second=(\d+)" )

	def __init__( self, dev ):
		self.interface	= dev.__if
		self.dev		= dev
		self.type		= self.dev.__class__.__name__
		self.info		= [ "Real Time Clock", "" ]
		
		if isinstance( self.interface, machine.I2C ):
			self.address	= dev.__adr
			self.dev_name	= self.type + "_on_I2C(0x%02X)" % (dev.__adr << 1)
		else:
			self.address	= dev.__cs
			self.dev_name	= self.type + "_on_SPI({})".format( dev.__cs )

	def parse( self, req ):
		if self.dev_name not in req:
			return None
	
		if "?" not in req:
			html	= self.page_setup()
		elif "set_current_time" in req:
			self.dev.datetime( machine.RTC().datetime() )
			html	= 'HTTP/1.0 200 OK\n\n'	# dummy
		elif "clear_alarm" in req:
			self.dev.clear_alarm()
			html	= 'HTTP/1.0 200 OK\n\n'	# dummy
		else:
			m	= self.regex_reg.match( req )
			if m:
				reg	= int( m.group( 1 ) )
				val	= int( m.group( 2 ) )

				self.dev.write_registers( reg, val )
				html	= 'HTTP/1.0 200 OK\n\n' + ujson.dumps( { "reg": reg, "val": val } )

			m	= self.regex_alarm.match( req )
			if m:
				alarm_time	= {
									"weekday"	: int( m.group( 1 ) ),
									"day"		: int( m.group( 2 ) ),
									"hours"		: int( m.group( 3 ) ),
									"minutes"	: int( m.group( 4 ) ),
									"seconds"	: int( m.group( 5 ) ),
							  }
				
				self.dev.clear_alarm()
				self.dev.alarm_int( "A", **alarm_time )
				html	= 'HTTP/1.0 200 OK\n\n'	# dummy

			else:
				html	= self.sending_data()

		return html

	def sending_data( self ):
		if ( "PCF2131" in self.type ):
			tsl	= self.dev.timestamp()
			ts	= self.dev.timestamp2str( tsl )
		else:
			ts	= None
		
		alm_ofst	= self.dev.REG_NAME.index( "Second_alarm" )
		reg			= self.dev.dump()
		alarm_flg	= True if "alarm" in self.dev.check_events( self.dev.interrupt_clear() ) else False
		alarm		= reg[ alm_ofst : alm_ofst + 5 ]
		td			= self.dev.__get_datetime_reg()
		
		td[ "weekday" ]	= self.WKDY[ td[ "weekday" ] ]
		td[ "month"   ]	= self.MNTH[ td[ "month"   ] ]
		td[ "str"   ]	 = "%04d %s %02d (%s) %02d:%02d:%02d" % \
							(td[ "year" ], td[ "month" ], td[ "day" ], td[ "weekday" ], \
							td[ "hours" ], td[ "minutes" ], td[ "seconds" ] )
		
		return 'HTTP/1.0 200 OK\n\n' + ujson.dumps( { "datetime": td, "reg": reg, "ts": ts, "alarm_flg": alarm_flg, "alarm": alarm } )

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
				<script>
					const	DEV_NAME	= '{% dev_name %}'
					const	REQ_HEADER	= '/' + DEV_NAME + '?';
					const	SOUND_DATA	= '{% sound %}';
					let		sound;

					if ( '' != SOUND_DATA )
						sound	= new Audio( SOUND_DATA );
					else
						sound	= null;
						
					/****************************
					 ****	time display
					 ****************************/
					 
					/******** getTimeAndShow ********/

					function getTimeAndShow() {
						let url	= REQ_HEADER
						ajaxUpdate( url, getTimeAndShowDone )
					}

					/******** getTimeAndShowDone ********/

					let prev_reg	= [];	//	to prevent refresh on user writing field
					let prev_alarm	= [];	//	to prevent refresh on user writing field
					let prev_alarm_flg	= false;	//	to prevent error of retrying open the dialog

					function getTimeAndShowDone() {
						let obj = JSON.parse( this.responseText )

						let elem = document.getElementById( "datetime" );
						elem.innerText = obj.datetime.str;
						//console.log( obj.ts )
						if ( obj.ts ) {
							let elem = document.getElementById( "timestamp" );
							elem.innerText = obj.ts;
						}

						for ( let i = 0; i < 5; i++ ) {
							let value	= obj.alarm[ i ];
							if ( value != prev_alarm[ i ] ) {
								document.getElementById( "alarmField" + i ).value	= ( value == 0x80 ) ? '--' : hex( value );
							}
						}
						prev_alarm	= obj.alarm;
												
						for ( let i = 0; i < obj.reg.length; i++ ) {
							let value	= obj.reg[ i ];
							if ( value != prev_reg[ i ] ) {
								document.getElementById('regField' + i ).value	= hex( value );
							}
						}
						prev_reg	= obj.reg;
						
						if ( obj.alarm_flg ) {
							document.getElementById( 'dialog' ).showModal();
							prev_alarm_flg	= true;
							
							if ( sound )
								sound.play();
							else
								console.log( 'Sound is not played' )
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

						let url	= REQ_HEADER + "reg=" + idx + "&val=" + value
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
						setInterval( getTimeAndShow, 1000 );
					});

					</script>

					<div class="header">
						<p>{% dev_link %} server</p>
						<p class="info">{% dev_info %}</p>
					</div>

					<div id="datetime" class="datetime"></div>

					<div>
						<input type="button" onclick="setCurrentTime();" value="Set current time" class="tmp_button"><br/>
		
						<script>
							function setCurrentTime( element ) {
								let url	= REQ_HEADER + 'set_current_time';
								ajaxUpdate( url );
							}
						</script>
					</div>

					<dialog class="alarm_dialog" id="dialog">
						DING! DING!  -- ALARM TRIGGERED --<br/><br/>
						<input type="button" onclick="clarAlarm();" value="Clear alarm" class="tmp_button"><br/>
					</dialog>
						
					<script>
						function clarAlarm( element ) {
							document.getElementById( 'dialog' ).close();
							prev_alarm_flg	= false
							
							let url	= REQ_HEADER + 'clear_alarm'
							ajaxUpdate( url );
						}
					</script>
				
					<div>

						<!-- alarm setting<br/> -->

						<table class="table_RTC_alarm">
							<tr class="reg_table_row">
								<td class="td_RTC_alarm reg_table_val">
									<table class="table_RTC_alarm">
										<tr class="reg_table_row">
											<td class="td_RTC_alarm reg_table_val"> weekday<input type="text" id="alarmField4" minlength=2 size=2 value="--" class="regfield">
											<td class="td_RTC_alarm reg_table_val"> day    <input type="text" id="alarmField3" minlength=2 size=2 value="--" class="regfield">
											<td class="td_RTC_alarm reg_table_val"> hour   <input type="text" id="alarmField2" minlength=2 size=2 value="--" class="regfield">
											<td class="td_RTC_alarm reg_table_val"> minute <input type="text" id="alarmField1" minlength=2 size=2 value="--" class="regfield">
											<td class="td_RTC_alarm reg_table_val"> second <input type="text" id="alarmField0" minlength=2 size=2 value="--" class="regfield">
										<t/d>
										</tr>
									</table>

								<td class="td_RTC_alarm reg_table_val">
									<input type="button" onclick="setAlarm();" value="Set alarm" class="tmp_button"><br/>
									<input type="button" onclick="clearAlarmSetting();" value="Clear alarm seting" class="tmp_button"><br/>

									<script>
										function setAlarm( element ) {
										
											let weekday = document.getElementById( "alarmField4" ).value;
											let day		= document.getElementById( "alarmField3" ).value;
											let hour	= document.getElementById( "alarmField2" ).value;
											let minute	= document.getElementById( "alarmField1" ).value;
											let second	= document.getElementById( "alarmField0" ).value;

											weekday	= ('--' == weekday) ? 80 : weekday;
											day		= ('--' == day)     ? 80 : day;
											hour	= ('--' == hour)    ? 80 : hour;
											minute	= ('--' == minute)  ? 80 : minute;
											second	= ('--' == second)  ? 80 : second;

											weekday	= '&weekday=' + weekday;
											day		= '&day='     + day;
											hour	= '&hour='    + hour;
											minute	= '&minute='  + minute;
											second	= '&second='  + second;

											let url	= REQ_HEADER + 'alarm' + weekday + day + hour + minute + second;
											ajaxUpdate( url );
										}
									</script>
								</td>
							</tr>
						</table>

						<script>
							function clearAlarmSetting( element ) {
								document.getElementById( "alarmField4" ).value	= '--';
								document.getElementById( "alarmField3" ).value	= '--';
								document.getElementById( "alarmField2" ).value	= '--';
								document.getElementById( "alarmField1" ).value	= '--';
								document.getElementById( "alarmField0" ).value	= '--';

								weekday	= '&weekday=' + 80;
								day		= '&day='     + 80;
								hour	= '&hour='    + 80;
								minute	= '&minute='  + 80;
								second	= '&second='  + 80;

								let url	= REQ_HEADER + 'alarm' + weekday + day + hour + minute + second;
								ajaxUpdate( url );
							}
						</script>
					</div>

					{% timestamp %}

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
		page_data[ "dev_name"  ]	= self.dev_name
		page_data[ "dev_type"  ]	= self.type
		page_data[ "dev_link"  ]	= '<a href="{}" target="_blank" rel="noopener noreferrer">{}</a>'.format( self.DS_URL[ self.type ], self.type )
		page_data[ "dev_info"  ]	= self.dev.info()
		page_data[ "mcu"       ]	= os.uname().machine
		page_data[ "reg_table" ]	= self.get_reg_table( 4 )
		page_data[ "timestamp" ]	= '<div id="timestamp" class="timestamp">timestamps<br/></div>' if "PCF2131" in self.type else ''
		page_data[ "style"     ]	= demo_lib.util.get_css()
		page_data[ "sound"     ]	= sound_data.get_sound()

		if len( page_data[ "sound" ] ) is 0:
			print( "####### DUT_RTC: No sound data loaded" )
		else:
			print( "####### DUT_RTC: Sound data loaded" )




		for key, value in page_data.items():
			html = html.replace('{% ' + key + ' %}', value )
		
		return html

	def get_reg_table( self, cols ):
		total	= len( self.dev.REG_NAME )
		rows	= (total + cols - 1) // cols

		s	 	= [ '<table class="table_RTC">' ]

		for y in range( rows ):
			s	 	+= [ '<tr class="reg_table_row">' ]
			for i in range( y, total, rows ):
				s	+= [ '<td class="td_RTC reg_table_name">{}</td><td class="td_RTC reg_table_val">0x{:02X}</td>'.format( self.dev.REG_NAME[ i ], i ) ]
				s	+= [ '<td class="td_RTC reg_table_val"><input type="text" onchange="updateRegField( this, {} )" id="regField{}" minlength=2 size=2 value="--" class="regfield"></td>'.format( i, i ) ]

			s	+= [ '</tr>' ]

		s	+= [ '</table>' ]
		return "\n".join( s )
