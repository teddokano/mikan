from	machine	import	Pin, I2C, SPI
from	utime	import	sleep

from	nxp_periph	import	SC16IS7xx

def main():
#	intf	= I2C( 0, freq = (400 * 1000) )
	intf	= SPI( 0, 1000 * 1000, cs = 0 )
	br		= SC16IS7xx( intf )
	
	br.info()
	
	while True:
		br.write( 0xAA )
		br.write( 0x55 )
		br.write( [ x for x in range( 8 ) ] )
		br.write( "abcdefg" )
		br.flush()
		br.sendbreak()
		if br.any():
			print( br.read() )

if __name__ == "__main__":
	main()
