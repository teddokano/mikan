#	MicroPython HTTP server sample code based on "http_server_simplistic.py".
#	https://github.com/micropython/micropython/blob/master/examples/network/http_server_simplistic.py
#
#	Based on simple HTTP server code, Trying LED ON/OFF via web
#	https://gist.github.com/teddokano/45b99cd906e63a23105ab427ae70d1dc
#	https://forum.micropython.org/viewtopic.php?t=1940#p10926
#
#	*** MEMO ***
#	  You may thonk the intefaceon web page may be better than this.
#	  A tggle button could be smarter interface.
#	  However I kept this interface to show very simple code.
#	  More attractive sample can be found at "remote_LED_dimmer.py"
#
#	Tedd OKANO / Released under the MIT license
#	15-Oct-2022
#	version	0.1

import	network
import	machine

from	nxp_periph	import	PCA9956B, LED

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


#HTML to send to browsers
CONTENT = b"""\
HTTP/1.0 200 OK

<!DOCTYPE html>
<html>
	<head>
		<title>MIMXRT1050 LED ON/OFF</title>
	</head>
	<body>
		<h2>A simple webserver to turning ON/OFF a LED with Micropython</h2>
		<form>
			LED0:
			<button name="LED" value="ON0" type="submit">ON</button>
			<button name="LED" value="OFF0" type="submit">OFF</button><br>
			LED1:
			<button name="LED" value="ON1" type="submit">ON</button>
			<button name="LED" value="OFF1" type="submit">OFF</button><br>
			LED2:
			<button name="LED" value="ON2" type="submit">ON</button>
			<button name="LED" value="OFF2" type="submit">OFF</button><br>
		</form>

		Hello #%d from MicroPython!
	</body>
</html>
"""

#Setup LED
i2c		= machine.I2C( 0, freq = (400 * 1000) )
led_c	= PCA9956B( i2c, address = 0x02 >> 1 )
led0	= LED( led_c, 0 )
led1	= LED( led_c, 1 )
led2	= LED( led_c, 2 )

def main( micropython_optimize=False ):
	ip_info	= start_network()

	s = socket.socket()

	ai = socket.getaddrinfo("0.0.0.0", 8080)
	print("Bind address info:", ai)
	addr = ai[0][-1]

	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.bind(addr)
	s.listen(5)
	print("Listening, connect your browser to http://{}:8080/".format( ip_info[0] ))

	counter = 0
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
		print("==== print(req) ====")
		print( req )
		
		if "/?LED=ON0" in req:
			led0.v	= 1.0
		elif "/?LED=OFF0" in req:
			led0.v	= 0.0
		elif "/?LED=ON1" in req:
			led1.v	= 1.0
		elif "/?LED=OFF1" in req:
			led1.v	= 0.0
		elif "/?LED=ON2" in req:
			led2.v	= 1.0
		elif "/?LED=OFF2" in req:
			led2.v	= 0.0

		while True:
			h = client_stream.readline()
			if h == b"" or h == b"\r\n":
				break
			print(h)
		client_stream.write( CONTENT % counter )

		client_stream.close()
		if not micropython_optimize:
			client_sock.close()
		counter += 1
		print()

main()
