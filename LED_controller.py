from	machine	import	I2C, SoftSPI
from	utime	import	sleep

from	nxp_periph	import	PCA9955B, PCA9956B, PCA9957, PCA9632, LED

def main():
	i2c		= I2C( 0, freq = (400 * 1000) )
	led_c	= PCA9632( i2c )	
	"""
	spi		= SoftSPI( baudrate = 100*1000, mosi = Pin( "D6" ), miso = Pin( "D3" ), sck = Pin( "D7" ) )
	cs		= Pin( "D4" )
	led_c	= PCA9957( spi, cs )
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
