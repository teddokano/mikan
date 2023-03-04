from nxp_periph.interface	import	I2C_target
from machine				import	I2C

def main():
	i2c			= I2C( 0, freq = (400 * 1000) )
	myInstance	= myClass( i2c )

	print( i2c.scan() )
	print( myInstance.do_something() )

class myClass( I2C_target ):
	DEFAULT_ADDR	= 0xAA
	REG_NAME		= ()

	def __init__( self, i2c, address = DEFAULT_ADDR ):
		super().__init__( i2c, address )
		
	def do_something( self ):
		return "hello " + self.__class__.__name__
		
if __name__ == "__main__":
	main()
