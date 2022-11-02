from	machine	import	Pin, I2C, SoftSPI, SPI
from	utime	import	sleep

from	nxp_periph	import	PCA9956B, PCA9955B, PCA9957

def main():
	i2c		= I2C( 0, freq = (400 * 1000) )
	led_c	= PCA9955B( i2c, address = 0x06 >> 1 )
	"""
	spi		= SPI( 0, 1000 * 1000, cs = 0 )
	led_c	= PCA9957( spi, setup_EVB = True )
	"""

	print( led_c.info() )
	led_c.dump_reg()

	led_c.gradation_channel_enable( [] )

	led_c.gradation_channel_enable( [ 4, 8, 12 ] )
	led_c.pwm(  0, 1.0 )
	led_c.pwm(  4, 1.0 )
	led_c.pwm(  8, 1.0 )
	led_c.pwm( 12, 1.0 )

	led_c.set_gradation( 0, 1.0, 0.5, up = True, down = True, on = 1, off = 1 )
	
	led_c.gradation_group_assign( [[0, 4, 8, 12 ], [1, 5, 9, 13 ], [2, 6, 10, 14 ], [3, 7, 11, 15]] )
#	led_c.gradation_group_assign( [[0, 1, 2, 3 ], [ 4,5,6,7 ], [8,9,10,11], [12,13,14,15]] )


	led_c.gradation_channel_enable( [ 4, 8, 12 ] )
	led_c.gradation_start( [ 0 ] )
	
	led_c.dump_reg()

	led_c.pwm( 0, 0.5 )
	while True:
		led_c.iref( 0, 0.5 )
		sleep( 0.1 )
		led_c.iref( 0, 0.0 )
		sleep( 0.1 )
	

if __name__ == "__main__":
	main()
