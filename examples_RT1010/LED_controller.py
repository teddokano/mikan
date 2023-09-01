from	machine	import	I2C, SoftI2C, SPI, SoftSPI
from	utime	import	sleep

if "i.MX RT1010 EVK" in os.uname().machine:
	from	nxp_periph.LED_controller	import	PCA9955B, PCA9956B, PCA9957, PCA9632, LED
else:
	from	nxp_periph	import	PCA9955B, PCA9956B, PCA9957, PCA9632

def main():
	"""
	if "i.MX RT1010 EVK" in os.uname().machine:
		i2c		= SoftI2C( sda = "A4", scl = "A5", freq = (400 * 1000) )
	else:
		i2c		= I2C( 0, freq = (400 * 1000) )
		
	led_c	= PCA9955B( i2c, address = 0xBC >> 1, setup_EVB = True )

	"""
	spi		= SPI( 0, 1000 * 1000, cs = 0 )
	led_c	= PCA9957( spi, setup_EVB = True )

	print( led_c.info() )
	led_c.pwm( 0, 0.5 )
	led_c.dump_reg()

	while True:
		led_c.pwm( 0, 0.5 )
		sleep( 0.1 )
		led_c.pwm( 0, 0.0 )
		sleep( 0.1 )

if __name__ == "__main__":
	main()
