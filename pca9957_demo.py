"""
Serial interface management library for MicroPython
Akifumi (Tedd) OKANO / Released under the MIT license

version	0.1 (01-Oct-2022)
"""

from	machine		import	Pin, SPI, SoftSPI
from	nxp_periph	import	PCA9957


def main():
	print( "Demo is running on {}".format( os.uname().machine ) )

	spi		= SoftSPI( baudrate = 100*1000, mosi = Pin( "D6" ), miso = Pin( "D3" ), sck = Pin( "D7" ) )
	cs		= Pin( "D4" )

	led_c	= PCA9957( spi, cs )

	print( led_c.info() )
	
	led_c.read_registers( "LEDOUT0", 6 )
	led_c.show_reg( "LEDOUT0" )
	led_c.dump_reg()
	
	while True:
		for i in range( led_c.CHANNELS ):
			for j in range( 2 ):
				led_c.pwm( i, 1.0 )
				sleep( 0.1 )
				led_c.pwm( i, 0.0 )
				sleep( 0.1 )

if __name__ == "__main__":
	from utime import sleep
	import	os
	import	math

	main()
