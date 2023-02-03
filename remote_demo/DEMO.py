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

from	nxp_periph	import	PCA9956B, PCA9955B, PCA9632, PCA9957, LED
from	nxp_periph	import	PCT2075, LM75B, P3T1085
from	nxp_periph	import	PCF2131, PCF85063
from	nxp_periph	import	PCAL6408, PCAL6416, PCAL6524, PCAL6534
from	nxp_periph	import	i2c_fullscan

from	demo_lib	import	DUT_LEDC, DUT_TEMP, DUT_RTC, DUT_GPIO
from	demo_lib	import	DUT_GENERALCALL, General_call
from	demo_lib	import	DUT_base

MEM_MONITORING	= False

def main( micropython_optimize = False ):
	print( "remote device demo" )
	print( "  http server is started working on " + os.uname().machine )
	print( "" )
	
	src_dir		= "demo_lib/"
	src_files	= os.listdir( src_dir )
	regex_file	= ure.compile( r"GET /(\S+)\sHTTP" )

	i2c			= machine.I2C( 0, freq = (400 * 1000) )
	spi			= machine.SPI( 0, 1000 * 1000, cs = 0 )

	pca9956b_0	= PCA9956B( i2c, 0x02 >>1 )
	pca9956b_1	= PCA9956B( i2c, 0x04 >>1 )
	pca9955b_0	= PCA9955B( i2c, 0x06 >>1 )
	pca9955b_1	= PCA9955B( i2c, 0x08 >>1 )
	pca9632		= PCA9632( i2c )
	pca9957		= PCA9957( spi, setup_EVB = True )
	pct2075		= PCT2075( i2c, setup_EVB = True  )
	pcf2131_i2c	= PCF2131( i2c )
	pcal6408	= PCAL6408( i2c, 0x21, setup_EVB = True )
	pcal6416	= PCAL6416( i2c, 0x20, setup_EVB = True )
	pcal6524	= PCAL6524( i2c, 0x22, setup_EVB = True )
	pcal6534	= PCAL6534( i2c, 0x23, setup_EVB = True )
#	pcf2131_spi	= PCF2131( spi )
#	pcf85063	= PCF85063( i2c )

	si2c		= machine.SoftI2C( sda = "D14", scl = "D15", freq = (400 * 1000) )
	p3t1085		= P3T1085( si2c )

	
	gene_call	= General_call( i2c )

	devices			= [	pca9956b_0,
						pca9956b_1,
						pca9955b_0,
						pca9955b_1,
						gene_call,
						pca9957,
						pca9632,
						pct2075,
						pcf2131_i2c,
						pcal6408, 
						pcal6416, 
						pcal6524, 
						pcal6534, 
#						pcf2131_spi,
#						pcf85063,
						p3t1085,
						]
	
	demo_harnesses	= [	DUT_LEDC,
						DUT_TEMP,
						DUT_RTC,
						DUT_GPIO,
						DUT_GENERALCALL,
						]
	
	dut_list	= get_dut_list( devices, demo_harnesses )

#	for d in dut_list:
#		print( d.info )
	
#	for i in i2c_fullscan( i2c ):
#		print( "0x%02X (0x%02X)" % ( i, i << 1 ) )
	
	ip_info	= start_network()

	s = socket.socket()

	ai = socket.getaddrinfo( "0.0.0.0", 8080 )
	addr = ai[0][-1]

	s.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
	s.bind( addr )
#	s.listen( 1 )
	s.listen( 5 )
	print("Listening, connect your browser to http://{}:8080/".format( ip_info[0] ))

	count	= 0

	while True:
		res = s.accept()
		client_sock = res[0]
		client_addr = res[1]
		print( "Client address: ", client_addr, end = "" )
		print( " / socket: ", client_sock )

		if not micropython_optimize:
			client_stream = client_sock.makefile("rwb")
		else:
			client_stream = client_sock

		req = client_stream.readline()
		print( "Request: \"{}\"".format( req.decode()[:-2] ) )

		for dut in dut_list:
			html	= dut.parse( req )
			if html:
				break

		if not html:
			m	= regex_file.match( req )
			if m and (fn	:= m.group( 1 ).decode()) and (fn in src_files):
				with open( src_dir + fn, "r" ) as f:
					html	 = ""
					html 	+= f.read()
					html	+= "\n"
			elif "GET / " in req:
				html	= page_setup( dut_list, i2c, live_only = True if "?live_only=True" in req else False )			
			else:
				html	= ""

		while True:
			h = client_stream.readline()
			if h == b"" or h == b"\r\n":
				break
		
		send_response( client_stream, html )

		client_stream.close()
		if not micropython_optimize:
			client_sock.close()

		if MEM_MONITORING:
			gc.collect()
			print( gc.mem_alloc() / 1024 )

		print()

def send_response( stream, str ):
	try:
		stream.write( "HTTP/1.0 200 OK\n\n" + str )
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


def start_network( port = 0, ifcnfg_param = "dhcp" ):
	print( "starting network" )

	lan = network.LAN( port )
	lan.active( True )

	print( "ethernet port %d is activated" % port )

	lan.ifconfig( ifcnfg_param )
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

main( micropython_optimize = True )
