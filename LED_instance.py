from	machine	import	I2C, SoftSPI
from	utime	import	sleep

from	nxp_periph	import	PCA9955B, PCA9956B, PCA9957, LED

def main():
	"""
	i2c		= I2C( 0, freq = (400 * 1000) )
	led_c	= PCA9956B( i2c )	
	"""
	spi		= SoftSPI( baudrate = 100*1000, mosi = Pin( "D6" ), miso = Pin( "D3" ), sck = Pin( "D7" ) )
	cs		= Pin( "D4" )
	led_c	= PCA9957( spi, cs )
	led		= LED( led_c, 1 )

	print( led_c.info() )
	
	while True:
		led.v	= 0.5
		sleep( 0.1 )
		led.v	= 0
		sleep( 0.1 )

if __name__ == "__main__":
	main()
