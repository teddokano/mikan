from	machine	import		SPI
from	utime	import		sleep
from	nxp_periph	import	PCA9957

ledd	= PCA9957( SPI( 0, 1000_000, cs = 0 ), iref = 0xFF )

print( ledd.info() )

while True:
	ledd.pwm( 0, 1.0 )
	sleep( 0.1 )
	ledd.pwm( 0, 0.0 )
	sleep( 0.1 )
