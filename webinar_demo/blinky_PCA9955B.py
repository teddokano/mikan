from	machine	import		I2C
from	utime	import		sleep
from	nxp_periph	import	PCA9955B

ledd	= PCA9955B( I2C( 0 ), address = 0xBC >> 1, iref = 0xFF )

print( ledd.info() )

while True:
	ledd.pwm( 0, 1.0 )
	sleep( 0.1 )
	ledd.pwm( 0, 0.0 )
	sleep( 0.1 )
