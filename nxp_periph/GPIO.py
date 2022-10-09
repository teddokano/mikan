"""
Temperature sensor operation library for MicroPython
Akifumi (Tedd) OKANO / Released under the MIT license

version	0.1 (09-Oct-2022)
"""
from nxp_periph.interface	import	I2C_target

class GPIO_base():
	"""
	An abstraction class to make user interface.
	"""

	def input( self ):
		return 	self.read_registers( self.__in, self.__np )

	def output( self, v ):
		self.write_registers( self.__out, v )

	def polarity( self, *args ):
		if 0 == len( args ):
			return self.read_registers( self.__pol, self.__np )
		else:
			self.write_registers( self.__pol, args[ 0 ] )

	def config( self, *args ):
		if 0 == len( args ):
			return self.read_registers( self.__cfg, self.__np )
		else:
			self.write_registers( self.__cfg, args[ 0 ] )

	@property
	def value( self ):
		"""
		Read port
	
		Returns
		-------
		list or int : port read value
			
		"""
		return self.input()

	@value.setter
	def value( self, v ):
		self.output( v )


class PCA9555( GPIO_base, I2C_target ):
	DEFAULT_ADDR	= 0x40 >> 1
	N_PORTS			= 2
	
	REG_NAME	= ( "Input_port_0", "Input_port_1",
					"Output_port_0", "Output_port_1",
					"Polarity_Inversion_port_0", "Polarity_Inversion_port_1",
					"Configuration_port_0", "Configuration_port_1"
					)

	def __init__( self, i2c, address = DEFAULT_ADDR ):
		super().__init__( i2c, address )
		self.__in	= "Input_port_0"
		self.__out	= "Output_port_0"
		self.__pol	= "Polarity_Inversion_port_0"
		self.__cfg	= "Configuration_port_0"
		self.__np	= self.N_PORTS

class PCA9554( GPIO_base, I2C_target ):
	DEFAULT_ADDR	= 0x40 >> 1
	N_PORTS			= 1
	
	REG_NAME	= ( "Input_Port",
					"Output_Port"
					"Polarity_Inversion",
					"Configuration"
					)

	def __init__( self, i2c, address = DEFAULT_ADDR ):
		super().__init__( i2c, address )
		self.__in	= "Input_Port"
		self.__out	= "Output_Port"
		self.__pol	= "Polarity_Inversion"
		self.__cfg	= "Configuration"
		self.__np	= self.N_PORTS

from	machine		import	Pin, I2C, SPI, SoftSPI, Timer

def main():
	i2c		= I2C( 0, freq = (400 * 1000) )
	gpio	= PCA9555( i2c )

	gpio.config( [ 0x00, 0xFF ] )

	while True:
		for i in range( 256 ):
			gpio.value	= [ i, i ]
		
		print( "port read = {}".format( gpio.value ), end = "\r" )

if __name__ == "__main__":
	main()
