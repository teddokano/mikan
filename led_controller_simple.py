from	machine	import	I2C
from	utime	import	sleep

from	nxp_periph	import	PCA9955B

def main():
	i2c		= I2C( 0, freq = (400 * 1000) )
	led_c	= PCA9955B( i2c )

	print( led_c )

	while True:
		led_c.pwm( 15, 1.0 )
		sleep( 0.1 )
		led_c.pwm( 15, 0.0 )
		sleep( 0.1 )
		
if __name__ == "__main__":
	main()
