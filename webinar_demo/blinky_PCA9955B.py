from	machine	import		I2C
from	utime	import		sleep
from	nxp_periph	import	PCA9955B

#
i2c		= I2C( 0, freq = (400 * 1000) )
ledd	= PCA9955B( i2c, address = 0xBC >> 1, setup_EVB = True )

print( ledd.info() )

while True:
	ledd.pwm( 0, 1.0 )
	sleep( 0.1 )
	ledd.pwm( 0, 0.0 )
	sleep( 0.1 )
