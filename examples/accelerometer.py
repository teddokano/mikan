from nxp_periph		import	FXOS8700, FXLS8974
from machine		import	I2C
from utime			import sleep


from	machine		import	Pin, SoftI2C

def main():
	i2c		= I2C( 0, freq = (400 * 1000) )
#	acc		= FXOS8700( i2c )
	acc		= FXLS8974( i2c, 0x19 )

	print( i2c.scan() )
	acc.dump_reg()

	while True:
		print( acc.xyz() )
		sleep( 0.5 )
		
if __name__ == "__main__":
	main()
