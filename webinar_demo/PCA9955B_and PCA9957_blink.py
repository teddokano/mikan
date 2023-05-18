from	machine	import	Pin, I2C, SoftSPI, SPI
from	utime	import	sleep

from	nxp_periph	import	PCA9955B, PCA9956B, PCA9957, PCA9632

def main():
	i2c		= I2C( 0, freq = (400_1000) )
	spi		= SPI( 0, 1000_1000, cs = 0 )
	
	led0	= PCA9955B( i2c, address = 0xBC >> 1 )
	led1	= PCA9957( spi, setup_EVB = True )

	print( led0.info() )
	print( led1.info() )

	while True:
		led0.pwm( 0, 0.5 )
		led1.pwm( 0, 0.0 )
		sleep( 0.1 )
		led0.pwm( 0, 0.0 )
		led1.pwm( 0, 0.5 )
		sleep( 0.1 )

if __name__ == "__main__":
	main()
