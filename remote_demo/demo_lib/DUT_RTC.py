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
import	demo_lib.util

class DUT_RTC():
	WKDY	= ( "Monday", "Tuesday", "Wednesday",
				"Thursday", "Friday", "Saturday", "Sunday" )
	MNTH	= ( "None", "January", "February", "March",
				"April", "May", "June", "July", "August",
				"September", "October", "Nobemver", "Decemver" )

	regex_reg	= ure.compile( r".*reg=(\d+)&val=(\d+)" )

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
		else:
			m	= self.regex_reg.match( req )
			if m:
				print( m.groups() )
				reg	= int( m.group( 1 ) )
				val	= int( m.group( 2 ) )

				self.dev.write_registers( reg, val )
				html	= 'HTTP/1.0 200 OK\n\n' + ujson.dumps( { "reg": reg, "val": val } )

			else:
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
						<p>{% dev_type %} server</p>
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
		page_data[ "dev_name"  ]	= self.dev_name
		page_data[ "dev_type"  ]	= self.type
		page_data[ "dev_info"  ]	= self.dev.info()
		page_data[ "mcu"       ]	= os.uname().machine
		page_data[ "reg_table" ]	= self.get_reg_table( 4 )
		page_data[ "style"     ]	= demo_lib.util.get_css()

		for key, value in page_data.items():
			html = html.replace('{% ' + key + ' %}', value )
		
		return html


	def sending_data( self ):
		reg	= self.dev.dump()
		td	= self.dev.__get_datetime_reg()
		
		td[ "weekday" ]	= self.WKDY[ td[ "weekday" ] ]
		td[ "month"   ]	= self.MNTH[ td[ "month"   ] ]
		td[ "str"   ]	 = "%04d %s %02d (%s) %02d:%02d:%02d" % \
							(td[ "year" ], td[ "month" ], td[ "day" ], td[ "weekday" ], \
							td[ "hours" ], td[ "minutes" ], td[ "seconds" ] )
		
		return 'HTTP/1.0 200 OK\n\n' + ujson.dumps( { "datetime": td, "reg": reg } )


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