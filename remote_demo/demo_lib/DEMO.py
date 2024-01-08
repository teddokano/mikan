import	network
import	ujson
import	machine
import	os
import	ure
import	gc
try:
    import usocket as socket
except:
    import socket
from utime import ticks_ms
from utime import sleep

from	nxp_periph	import	PCA9956B, PCA9955B, PCA9632, PCA9957, LED
from	nxp_periph	import	PCT2075, LM75B, P3T1755, P3T1085
from	nxp_periph	import	PCF2131, PCF85063
from	nxp_periph	import	PCAL6408, PCAL6416, PCAL6524, PCAL6534
from	nxp_periph	import	FXOS8700, FXLS8974
from	nxp_periph	import	NAFE13388
from	nxp_periph	import	i2c_fullscan

from	demo_lib	import	DUT_LEDC, DUT_TEMP, DUT_RTC, DUT_GPIO, DUT_ACC, DUT_AFE
from	demo_lib	import	DUT_GENERALCALL, General_call
from	demo_lib	import	DUT_base

from	demo_lib.I2C_Character_LCD	import	AE_AQM0802

NETWORK_TIMEOUT	= False
MEM_MONITORING	= False
# MEM_MONITORING	= True	###

def demo( ip = "dhcp" ):
	print( "remote device demo" )
	print( "  http server is started working on " + os.uname().machine )
	print( "" )
	
	src_dir			= "demo_lib/"
	regex_file		= ure.compile( r"GET /(\S+)\sHTTP" )
	regex_suffix	= ure.compile( r".*\.(.*)" )


	if "i.MX RT1170 EVK" in os.uname().machine:
		i2c		= machine.I2C( 2, freq = (400_000) )
		spi		= machine.SPI( 0, 1000_000, cs = 0 )
		si2c	= machine.I2C( 0, freq = (400_000) )
		ep_num	= 1	# Ethernet port selection. 1 for 1G port, 0 for 100M port
	else:
		i2c		= machine.I2C( 0, freq = (400_000) )
		spi		= machine.SPI( 0, 1000_000, cs = 0 )
		
		# for NAFE13388
		#spi		= machine.SPI( 0, 1000_000, cs = 0, phase = 1 )
		
		si2c	= machine.SoftI2C( sda = "D14", scl = "D15", freq = (400_000) )
		ep_num	= 0
	
	devices			= [
						PCA9956B( i2c, 0x02 >>1 ),
						PCA9956B( i2c, 0x04 >>1 ),
						PCA9955B( i2c, 0x06 >>1 ),
						PCA9955B( i2c, 0x08 >>1 ),
						PCA9955B( i2c, 0xBC >>1 ),
						PCA9632( i2c ),
						PCA9957( spi, setup_EVB = True ),
						PCT2075( i2c, setup_EVB = True  ),
						PCF2131( i2c ),
#						PCAL6408( i2c, 0x21, setup_EVB = True ),
						PCAL6416( i2c, 0x20, setup_EVB = True ),
#						PCAL6524( i2c, 0x22, setup_EVB = True ),
#						PCAL6534( i2c, 0x22, setup_EVB = True ),
#						PCF2131( spi ),
#						PCF85063( i2c ),
#						P3T1085( si2c ),
#						FXLS8974( i2c, address = 0x18 ),
#						NAFE13388( spi ),
						FXLS8974( i2c, address = 0x18 ),
						FXOS8700( i2c ),
#						P3T1755( i2c ),
						General_call( i2c ),
						]
	
	demo_harnesses	= [	DUT_LEDC,
						DUT_TEMP,
						DUT_RTC,
						DUT_GPIO,
						DUT_ACC,
						DUT_AFE,
						DUT_GENERALCALL,
						]
	
	lcd_panel	= AE_AQM0802( si2c )
	lcd_panel.print( [ "Hello", "mikan" ] )
	
	dut_list	= get_dut_list( devices, demo_harnesses )

#	for d in dut_list:
#		print( d.info )
	
#	for i in i2c_fullscan( i2c ):
#		print( "0x%02X (0x%02X)" % ( i, i << 1 ) )

	ip_info	= start_network( port = ep_num, ifcnfg_param = ip, lcd = lcd_panel )
#	print( ip_info )

	s = socket.socket()
	
	if NETWORK_TIMEOUT:
		s.settimeout( 1000 )
		
	ai = socket.getaddrinfo( "0.0.0.0", 80 )
	addr = ai[0][-1]

	s.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
	s.bind( addr )
	s.listen( 10 )
	print("Listening, connect your browser to http://{}/".format( ip_info[0] ))

	lcd_panel.print( f"{ip_info[0]}" )
	
	count	= 0
	
	while True:
		if NETWORK_TIMEOUT:
			try:
				client_stream, client_addr = s.accept()
			except:
				# print( "*", end = "" )
				continue
		else:
			client_stream, client_addr = s.accept()

		e_time	= elapsed_time( ticks_ms() ) ###
		# e_time.enable	= True
		
		lcd_panel.backlight( False )
		
		print( f"[{count}] : client address: {client_addr} / socket: {client_stream}" )
		count	+= 1

		try:
			req = client_stream.readline()
		except:
			print( "ECONNABORTED" )
			client_stream.close()
			continue

		e_time.show( "readline done" ) ###
		print( "Request: \"{}\"".format( req.decode()[:-2] ) )

		server	= "mikan"
		content_type	= "text/html"

		for dut in dut_list:
			html	= dut.parse( req )
			if html:
				break

		if (not html) and ("server_response_time_test" in req):
			html	= "response for server_response_time_test"

		if not html:
			m	= regex_file.match( req )
			if m and (fn	:= m.group( 1 ).decode()):
				try:
					ext	= regex_suffix.match( fn ).group( 1 )
					content_type	= ext_content[ ext ]
				except:
					pass

				try:
					with open( src_dir + fn, "rb" ) as f:
						html 	= f.read()					
				except OSError as e:
					html = None

			elif "GET / " in req:
				html	= page_setup( dut_list, i2c, live_only = True if "?live_only=True" in req else False )			
			else:
				html	= ""

		while True:
			h = client_stream.readline()
			if h == b"" or h == b"\r\n":
				break
		
		send_response( client_stream, html, content_type )
		client_stream.close()
		
		e_time.show( "before gc" ) ###

		if MEM_MONITORING:
			gc.collect()
			print( "heap used {}".format( gc.mem_alloc() / 1024 ) )
			print( "heap free {}".format( gc.mem_free()  / 1024 ) )
		else:
			pass
			#print( "heap used {}".format( gc.mem_alloc() / 1024 ) )
			#print( "heap free {}".format( gc.mem_free()  / 1024 ) )

		e_time.show( "end" ) ###
		print()

def send_response( stream, content, content_type ):
	try:
		if None == content:
			stream.write( "HTTP/1.0 404 NOT FOUND\n\nFile Not Found" )
		else:
			stream.write( "HTTP/1.0 200 OK\nServer:mikan\nContent-Type: {}\n\n".format( content_type ) )
			stream.write( content )
	except OSError as e:
		print( "!!! OSError:", e.args )

def get_dut_list( devices, demo_harnesses ):
	list	= []

	for dev in devices:
		if dev.__class__ == General_call:
			last_dut	= DUT_GENERALCALL( dev )
			continue
	
		for dh in demo_harnesses:
			if issubclass( dev.__class__, dh.APPLIED_TO ):
				list	+= [ dh( dev ) ]

	return list + [ last_dut ]

def start_network( *, port = 0, ifcnfg_param = "dhcp", lcd = None ):
	print( "starting network" )

	try:
		lan = network.LAN( port )
	except OSError as e:
		if lcd is not None:
			lcd.print( [ "No LAN", " cable?" ] )
		error_loop( 2, "Check LAN cable connection. OSError:{}".format( e.args ) )	# infinite loop inside of this finction
		
	lan.active( True )
	print( "ethernet port %d is activated" % port )

	try:
		lan.ifconfig( ifcnfg_param )
	except OSError as e:
		if lcd is not None:
			lcd.print( [ "DHCP", " fail :(" ] )
		error_loop( 3, "Can't get/set IP address. Tried to set {}. OSError:{}".format( ifcnfg_param, e.args ) )	# infinite loop inside of this finction

	return lan.ifconfig()

class DEMO( DUT_base ):
	def __init__( self ):
		super().__init__( None )

def page_setup( dut_list, i2c, live_only = False ):
	db	= DEMO()

	db.page_data[ "dev_name"          ]	= "GENERAL"

	table, links	= page_table( dut_list, live_only = live_only )
	
	db.page_data[ "all_links"         ]	= links
	db.page_data[ "front_page_table"  ]	= table
	db.page_data[ "filtering_list"    ]	= filter_setting( live_only )
	db.page_data[ "i2c_scan"          ]	= i2c_scan_table( i2c )

	return db.load_html()

def filter_setting( filtering ):
	if filtering:
		return '<a href="/">show all device(s)</a>'
	else:
		return '<a href="/?live_only=True">live device(s) only</a>'
	

def page_table( dut_list, live_only = False ):
	s	 = [ '<table>' ]
	l	 = []

	s	+= [ '<tr>' ]
	s	+= [ '<td class="table_header"></td>' ]
	s	+= [ '<td class="table_header">device type</td>' ]
	s	+= [ '<td class="table_header">address</td>' ]
	s	+= [ '<td class="table_header">live?</td>' ]
	s	+= [ '<td class="table_header">family</td>' ]
	s	+= [ '<td class="table_header">info</td>' ]
	s	+= [ '<td class="table_header">interface</td>' ]
	s	+= [ '</tr>' ]


	for dut in dut_list[ :-1 ]:	#	ignore last DUT. It's a general call (virtual) device
		if "I2C" in str( dut.interface ):
			live	= dut.dev.ping()
		else:
			live	= None

		if live_only and (live is False):
			continue

		s	+= [ '<tr><td class="reg_table_name">{}</td>'.format( dut.symbol ) ]

		if live is not False:
			s	+= [ '<td class="reg_table_name"><a href="/{}" target="{}">{}</a></td>'.format( dut.dev_name, dut.dev_name, dut.type ) ]
			l	+= [ "'" + dut.dev_name + "'" ]
		else:
			s	+= [ '<td class="reg_table_name"><font color="#C0C0C0">{}</font></td>'.format( dut.type ) ]
		
		if dut.address:
			s	+= [ '<td class="reg_table_name">0x%02X (0x%02X)</td>' % ( dut.address, dut.address << 1 ) ]
		else:
			s	+= [ '<td class="reg_table_name">n/a</td>' ]

		s	+= [ '<td class="reg_table_name {}">{}</td>'.format( "Red_cell" if live is False else "Green_cell", live ) ]
		s	+= [ '<td class="reg_table_name">{}</td>'.format( dut.info[ 0 ] ) ]
		s	+= [ '<td class="reg_table_name">{}</td>'.format( dut.info[ 1 ] ) ]
		s	+= [ '<td class="reg_table_name">{}</td>'.format( dut.interface ) ]
		s	+= [ '</tr>' ]
		
	s	+= [ '</table>' ]

	return "\n".join( s ), ", ".join( l )

def i2c_scan_table( i2c ):
	scan_result	= i2c_fullscan( i2c )
	s	 = [ '<table>' ]
	s	+= [ '<tr>' ]
	s	+= [ '<td class="table_header">0x</td>' ]
	for x in range( 16 ):
		s	+= [ '<td class="table_header">x{:01X}</td>'.format( x ) ]
	s	+= [ '</tr>' ]
	
	for y in range( 0, 128, 16 ):
		s	+= [ '<tr>' ]
		s	+= [ '<td class="table_header">{:01X}x</td>'.format( y >> 4 ) ]

		for x in range( 16 ):
			adr  = y + x
			s	+= [ '<td class="table_i2c_val"><font color="{}">{:02X}({:02X})</font></td>'.format( '#000000' if adr in scan_result else '#EEEEEE', adr, adr << 1 ) ]
		s	+= [ '</tr>' ]
	
	s	+= [ '</table>' ]

	return "\n".join( s )

from utime import sleep

def error_loop( n, message ):
	led		= machine.Pin( "D4", machine.Pin.OUT )
	pattern	= [ 0, 1 ] * n + [ 1 ] * 4
	
	for i in range( 3 ):
		print( "**** ERROR ****" )
		
	print( message )
		
	while True:
		for p in pattern:
			led.value( p )
			sleep( 0.1 )

class elapsed_time:
	def __init__( self, start ):
		self.start	= start
		self.enable	= False
	def show( self, m ):
		if self.enable:
			print( m, end = ": " )
			print( ticks_ms() - self.start )
		else:
			pass

ext_content	= {	"css" : "text/css",
				"html": "text/html",
				"js"  : "text/javascript",
				"png" : "image/png",
				"jpg" : "image/jpg",
				"ico" : "image/ico",
				}

def main():
	demo( ip = "dhcp" )
#	demo( ip = ( "10.0.0.99", "255.255.255.0", "10.0.0.1", "8.8.8.8" ) )

if __name__ == "__main__":
	main()
