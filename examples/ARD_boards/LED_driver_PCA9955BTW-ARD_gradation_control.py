from	machine	import	Pin, I2C
from	utime	import	sleep
from	nxp_periph	import	PCA9955B

i2c		= I2C( 0, freq = (400 * 1000) )
led_c	= PCA9955B( i2c, address = 0xBC >> 1, setup_EVB = True )

enabling_channel	= (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14)
groups				= ( (0, 4, 8), (1, 5, 6), (2, 3, 7), (9, 10, 11, 12, 13, 14) )

manual_blink_ch		= 15

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

print( "rgb_cycle_time   = %f" % rgb_cycle_time   )
print( "white_cycle_time = %f" % white_cycle_time )

led_c.gradation_start( 0 )
sleep( rgb_cycle_time / 3 )
led_c.gradation_start( 1 )
sleep( rgb_cycle_time / 3 )
led_c.gradation_start( 2 )

while True:
	led_c.gradation_start( [ 3 ], continuous = False )			# single shot
	
	led_c.iref( manual_blink_ch, 0.1 )
	sleep( 0.1 )
	led_c.iref( manual_blink_ch, 0.0 )
	sleep( 0.1 )
