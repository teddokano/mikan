from	machine	import	I2C, SoftI2C, SPI, SoftSPI
from	utime	import	sleep

if "i.MX RT1010 EVK" in os.uname().machine:
	from	nxp_periph.LED_controller	import	PCA9955B, PCA9956B, PCA9957, PCA9632, LED
else:
	from	nxp_periph	import	PCA9955B, PCA9956B, PCA9957, PCA9632

IREF_INIT	= 0x10

def main():
	if "i.MX RT1010 EVK" in os.uname().machine:
		i2c		= SoftI2C( sda = "A4", scl = "A5", freq = (400 * 1000) )
	else:
		i2c		= I2C( 0, freq = (400 * 1000) )
		
	led_c	= PCA9955B( i2c, 0xBC >>1, iref = IREF_INIT, setup_EVB = True )	
	"""
	spi		= SPI( 0, 1000 * 1000, cs = 0 )
	led_c	= PCA9957( spi, setup_EVB = True )
	"""

	led		= LED( led_c, 1 )

	print( led_c.info() )
	
	while True:
		led.v	= 0.5
		sleep( 0.1 )
		led.v	= 0
		sleep( 0.1 )

if __name__ == "__main__":
	main()
