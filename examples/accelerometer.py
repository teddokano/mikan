from nxp_periph		import	FXOS8700
from machine		import	I2C
from utime import sleep
from ustruct import unpack

def main():
	i2c		= I2C( 0, freq = (400 * 1000) )
	acc		= FXOS8700( i2c )

	print( 	i2c.scan() )
	acc.dump_reg()

	while True:
		print( acc.xyz() )
		sleep( 0.5 )
		
if __name__ == "__main__":
	main()
