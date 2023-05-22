from	machine	import		Pin, I2C, SoftSPI, SPI
from	utime	import		sleep
from	nxp_periph	import	PCA9955B, PCA9957

#USE_PCA9955B	= True
USE_PCA9955B	= False

def main():
	
	if USE_PCA9955B:
		i2c		= I2C( 0, freq = (400_000) )
		led_c	= PCA9955B( i2c, address = 0x06 >> 1 )
		
		enabling_channel	= [ 1, 2, 3, 5, 6, 7, 9, 10, 11, 13, 14, 15 ]
		groups				= [ [ 1, 5, 9, 13 ], [ 2, 6, 10, 14 ], [ 3, 7, 11, 15 ], [ 0, 4, 8, 12 ] ]

		manual_blink_ch		= 0
	else:
		spi		= SPI( 0, 1000 * 1000, cs = 0 )
		led_c	= PCA9957( spi, setup_EVB = True )

		enabling_channel	= [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22 ]
		groups				= [ [ 0, 3, 6, 9 ], [ 1, 4, 7, 10 ], [ 2, 5, 8, 11 ], [ 12, 13, 14, 15 ], [ 16, 17, 18, 19 ], [ 20, 21, 22, 23 ] ]

		manual_blink_ch		= 23

	print( led_c.info() )

	all	= [ 1.0 for i in range( led_c.CHANNELS ) ]
	led_c.pwm( all )

	led_c.gradation_channel_enable( enabling_channel )
	led_c.gradation_group_assign( groups )

	#	RGB gradation on group 0, 1, 2
	rgb_cycle_time	= led_c.set_gradation( 0, 1.0, 1, up = True, down = True, on = 0, off = 1 )
	led_c.set_gradation( 1, 1.0, 1, up = True, down = True, on = 0, off = 1 )
	led_c.set_gradation( 2, 1.0, 1, up = True, down = True, on = 0, off = 1 )

	#	White gradation on group 3
	white_cycle_time	= led_c.set_gradation( 3, 1.0, 6, up = False, down = True, on = 0, off = 0 )
	
	if not USE_PCA9955B:
		led_c.set_gradation( 4, 1.0, 6, up = True, down = False, on = 0, off = 0.0 )
		led_c.set_gradation( 5, 1.0, 3, up = True, down = True, on = 0, off = 0.0 )
	
	print( "rgb_cycle_time   = %f" % rgb_cycle_time   )
	print( "white_cycle_time = %f" % white_cycle_time )

	led_c.gradation_start( 0 )
	sleep( rgb_cycle_time / 3 )
	led_c.gradation_start( 1 )
	sleep( rgb_cycle_time / 3 )
	led_c.gradation_start( 2 )
	
	while True:
		if USE_PCA9955B:
			led_c.gradation_start( [ 3 ], continuous = False )			# single shot
		else:
			led_c.gradation_start( [ 3, 4, 5 ], continuous = False )	# single shot
		
		led_c.iref( manual_blink_ch, 0.5 )
		sleep( 3 )
		led_c.iref( manual_blink_ch, 0.0 )
		sleep( 3 )
	

if __name__ == "__main__":
	main()
