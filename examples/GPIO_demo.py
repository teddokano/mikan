from	machine		import	I2C
from	nxp_periph	import	PCA9555
import	utime

def main():
	i2c		= I2C( 0, freq = (400 * 1000) )
	gpio	= PCA9555( i2c )

	#	port0 is output, port1 is input
	#	check operation by connecting port0 pin to port1 pin
	gpio.config( [ 0x00, 0xFF ] )

	while True:
		for i in range( 256 ):
			gpio.value	= [ i, i ]
			utime.sleep( 0.1 )
			r	= gpio.value
			print( "port read = {}".format( [ "{:08b}".format( i ) for i in r ] ), end = "\r" )

if __name__ == "__main__":
	main()
