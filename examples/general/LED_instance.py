from	machine	import	I2C, SoftSPI, SPI
from	utime	import	sleep

from	nxp_periph	import	PCA9955B, PCA9956B, PCA9957, LED

def main():
	i2c		= I2C( 0, freq = (400 * 1000) )
	led_c	= PCA9956B( i2c )	
	"""
	spi		= SPI( 0, 1000 * 1000, cs = 0 )
	led_c	= PCA9957( spi, setup_EVB = True )
	"""

	led		= LED( led_c, 1 )

	print( led_c.info() )
	
	while True:
		led.v	= 0.5
		sleep( 0.1 )
		led.v	= 0
		sleep( 0.1 )

if __name__ == "__main__":
	main()
