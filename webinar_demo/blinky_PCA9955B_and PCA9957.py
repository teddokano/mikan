from	machine	import		I2C, SPI
from	utime	import		sleep
from	nxp_periph	import	PCA9955B, PCA9957

i2c		= I2C( 0, freq = (400_000) )
spi		= SPI( 0, 1000_000, cs = 0 )

led0	= PCA9955B( i2c, address = 0xBC >> 1, iref = 0xFF )
led1	= PCA9957( spi, iref = 0xFF )

print( led0.info() )
print( led1.info() )

while True:
	led0.pwm( 0, 1.0 )
	led1.pwm( 0, 0.0 )
	sleep( 0.1 )
	led0.pwm( 0, 0.0 )
	led1.pwm( 0, 1.0 )
	sleep( 0.1 )

