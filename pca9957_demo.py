"""
Serial interface management library for MicroPython
Akifumi (Tedd) OKANO / Released under the MIT license

version	0.1 (01-Oct-2022)
"""
import	os
import	math
from 	utime		import	sleep

from	machine		import	Pin, SPI, SoftSPI
from	nxp_periph	import	PCA9957


def main():
	print( "Demo is running on {}".format( os.uname().machine ) )

	spi		= SoftSPI( baudrate = 100*1000, mosi = Pin( "D6" ), miso = Pin( "D3" ), sck = Pin( "D7" ) )
	cs		= Pin( "D4" )

	led_c	= PCA9957( spi, cs )

	print( led_c.info() )
	led_c.dump_reg()

	simple( led_c )
	demo( led_c )

def simple( led_c ):
	while True:
		for i in range( led_c.CHANNELS ):
			for j in range( 2 ):
				led_c.pwm( i, 1.0 )
				sleep( 0.1 )
				led_c.pwm( i, 0.0 )
				sleep( 0.1 )

def demo( led_ctlr ):
	SAMPLE_LENGTH	= 60
	COLORS			= 3
	N_LED_UNIT		= 4

	print( "test_harness_0 working N_LED_UNIT={}".format( N_LED_UNIT ) )

	pattern	= [ 0.5 - 0.5 * math.cos( 2 * math.pi * x / SAMPLE_LENGTH ) for x in range( SAMPLE_LENGTH ) ]
#	pattern	= [ int( x * x * 255.0 ) for x in pattern ]
	pattern	= [ x * x for x in pattern ]
	ch_ofst	= SAMPLE_LENGTH // N_LED_UNIT

	data		= [ 0 ]	* led_ctlr.CHANNELS
	
	while True:
		for lum in pattern:
			print( lum )
			led_ctlr.pwm( 0, lum )
			sleep( 0.02 )



if __name__ == "__main__":

	main()
