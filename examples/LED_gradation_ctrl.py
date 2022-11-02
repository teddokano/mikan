from	machine	import	Pin, I2C, SoftSPI, SPI
from	utime	import	sleep

from	nxp_periph	import	PCA9956B, PCA9955B, PCA9957

def main():
	"""
	i2c		= I2C( 0, freq = (400 * 1000) )
	led_c	= PCA9955B( i2c, address = 0x06 >> 1 )
	"""
	spi		= SPI( 0, 1000 * 1000, cs = 0 )
	led_c	= PCA9957( spi, setup_EVB = True )

	print( led_c.info() )
	led_c.dump_reg()

	led_c.gradation_channel_enable( [ 1, 2, 3, 5, 6, 7, 9, 10, 11, 13, 14, 15 ] )
	all	= [ 1.0 for i in range( led_c.CHANNELS ) ]
	led_c.pwm( all )

	cycle_time	= led_c.set_gradation( 0, 1.0, 1, up = True, down = True, on = 0, off = 1 )
	led_c.set_gradation( 1, 1.0, 1, up = True, down = True, on = 0, off = 1 )
	led_c.set_gradation( 2, 1.0, 1, up = True, down = True, on = 0, off = 1 )
	
	led_c.gradation_group_assign( [[1, 5, 9, 13 ], [2, 6, 10, 14 ], [3, 7, 11, 15]] )

	print( cycle_time )

	led_c.gradation_start( [ 0 ] )
	sleep( cycle_time / 3 )
	led_c.gradation_start( [ 1 ] )
	sleep( cycle_time / 3 )
	led_c.gradation_start( [ 2 ] )
	
	led_c.dump_reg()

	led_c.pwm( 0, 0.5 )
	while True:
		led_c.iref( 0, 0.5 )
		sleep( 0.1 )
		led_c.iref( 0, 0.0 )
		sleep( 0.1 )
	

if __name__ == "__main__":
	main()
