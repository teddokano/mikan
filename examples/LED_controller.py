from	machine	import	Pin, I2C, SoftSPI, SPI
from	utime	import	sleep

from	nxp_periph	import	PCA9955B, PCA9956B, PCA9957, PCA9632

def main():
	i2c		= I2C( 0, freq = (400 * 1000) )
	led_c	= PCA9956B( i2c, address = 0x02 >> 1 )
	"""
	spi		= SPI( 0, 1000 * 1000 )
	led_c	= PCA9957( spi, setup_EVB = True )
	"""

	print( led_c.info() )
	led_c.dump_reg()

	while True:
		led_c.pwm( 0, 0.5 )
		sleep( 0.1 )
		led_c.pwm( 0, 0.0 )
		sleep( 0.1 )

if __name__ == "__main__":
	main()
