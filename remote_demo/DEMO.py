import	network
import	ujson
import	machine
import	os
import	ure
try:
    import usocket as socket
except:
    import socket

from	nxp_periph	import	PCA9956B, PCA9955B, PCA9632, PCA9957, LED
from	nxp_periph	import	PCT2075, LM75B
from	nxp_periph	import	PCF2131, PCF85063
from	nxp_periph	import	i2c_fullscan

from	demo_lib	import	DUT_LEDC, DUT_TEMP, DUT_RTC
from	demo_lib	import	DUT_GENERALCALL, General_call

import	demo_lib.utils	as utils


def main( micropython_optimize = False ):
	print( "remote device demo" )
	print( "  http server is started working on " + os.uname().machine )
	print( "" )

	i2c			= machine.I2C( 0, freq = (400 * 1000) )
	spi			= machine.SPI( 0, 1000 * 1000, cs = 0 )

	pca9956b_0	= PCA9956B( i2c, 0x02 >>1 )
	pca9956b_1	= PCA9956B( i2c, 0x04 >>1 )
	pca9955b	= PCA9955B( i2c, 0x06 >>1 )
	pca9632		= PCA9632( i2c )
	pca9957		= PCA9957( spi, setup_EVB = True )
	pct2075		= PCT2075( i2c, setup_EVB = True  )
	pcf2131_i2c	= PCF2131( i2c )
	pcf2131_spi	= PCF2131( spi )
	pcf85063	= PCF85063( i2c )
	
	gene_call	= General_call( i2c )

	devices			= [	pca9956b_0,
						pca9956b_1,
						pca9955b,
						gene_call,
						pca9632,
						pca9957,
						pct2075,
						pcf2131_i2c,
						pcf2131_spi,
						pcf85063,
						]
	
	demo_harnesses	= [	DUT_LEDC,
						DUT_TEMP,
						DUT_RTC,
						DUT_GENERALCALL,
						]
	
	dut_list	= get_dut_list( devices, demo_harnesses )
	
#	for i in i2c_fullscan( i2c ):
#		print( "0x%02X (0x%02X)" % ( i, i << 1 ) )
	
	ip_info	= start_network()

	s = socket.socket()

	ai = socket.getaddrinfo( "0.0.0.0", 8080 )
	addr = ai[0][-1]

	s.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
	s.bind( addr )
	s.listen( 1 )
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
			html	= page_setup( dut_list )

		while True:
			h = client_stream.readline()
			if h == b"" or h == b"\r\n":
				break
		
		try:
			client_stream.write( html )
		except OSError as e:
			print( "!!! OSError:", e.args )
		
		client_stream.close()
		if not micropython_optimize:
			client_sock.close()

		print()

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

def page_setup( dut_list ):
	html	= "HTTP/1.0 200 OK\n\n{% html %}"

	page_data	= {}
	page_data[ "dev_name"          ]	= "GENERAL"
	page_data[ "front_page_table"  ]	= page_table( dut_list )
	page_data[ "signature"         ]	= utils.page_signature()

	files	= [	[	"html",		"demo_lib/DEMO"		],
				[	"css", 		"demo_lib/DEMO"		],
				[	"js",		"demo_lib/general",
								"demo_lib/DEMO" 	]
			  ]

	html	= utils.file_loading( html, files )

	for key, value in page_data.items():
		html = html.replace('{% ' + key + ' %}', value )
	
	return html

def page_table( dut_list ):
	s	 = [ '<table>' ]

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
		s	+= [ '<tr>' ]
		
		if "I2C" in str( dut.interface ):
#			dut.dev.ping()
#			live	= dut.dev.live
			live	= dut.dev.ping()

		else:
			live	= None

		s	+= [ '<td class="reg_table_name">{}</td>'.format( dut.symbol ) ]

		if live is not False:
			s	+= [ '<td class="reg_table_name"><a href="/{}" target="_blank" rel="noopener noreferrer">{}</a></td>'.format( dut.dev_name, dut.type ) ]
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
	return "\n".join( s )

main()


