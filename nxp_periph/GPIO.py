from nxp_periph.interface	import	I2C_target

class GPIO_base():
	"""
	An abstraction class to make user interface.
	"""

	def input( self ):
		"""
		read input
		
		Returns
		-------
		int or list : port value
			It returns an integer value if 8 bit GPIO.
			Returns a list if the GPIO has multiple ports. First value is for port-0

		"""

		return 	self.read_registers( self.__in, self.__np )

	def output( self, v ):
		"""
		set output
		
		Parameters
		----------
		int or list : port value
			It takes an integer value if 8 bit GPIO.
			Takes a list if the GPIO has multiple ports. First value is for port-0

		"""
		self.write_registers( self.__out, v )

	def polarity( self, *args ):
		"""
		set/read polarity
		
		Parameters
		----------
		int or list : port value for setting
			When this method takes 1 argument, the value is set in register
			It takes an integer value if 8 bit GPIO.
			Takes a list if the GPIO has multiple ports. First value is for port-0

		Returns
		-------
		int or list : port value
			When this method takes no argument, the value is read from register
			It returns an integer value if 8 bit GPIO.
			Returns a list if the GPIO has multiple ports. First value is for port-0

		"""
		if 0 == len( args ):
			return self.read_registers( self.__pol, self.__np )
		else:
			self.write_registers( self.__pol, args[ 0 ] )

	def config( self, *args ):
		"""
		set/read configuration
		
		Parameters
		----------
		int or list : port value for setting
			When this method takes 1 argument, the value is set in register
			It takes an integer value if 8 bit GPIO.
			Takes a list if the GPIO has multiple ports. First value is for port-0

		Returns
		-------
		int or list : port value
			When this method takes no argument, the value is read from register
			It returns an integer value if 8 bit GPIO.
			Returns a list if the GPIO has multiple ports. First value is for port-0

		"""
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
	"""
	PCA9555: 16 bit GPIO expander
	
	A device class for an industry standard 16 bit GPIO expander
	This class can operate its family devices of
	  PCA9555A and PCA9539
	
	Parameters
	----------
	i2c		: I2C instance
	address	: int, option
	
	Returns
	-------
	PCA9555 object
	
	"""
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
	"""
	PCA9554: 8 bit GPIO expander
	
	A device class for an industry standard 8 bit GPIO expander
	This class can operate its family devices of
	  PCA9554A, PCA9554B, PCA954C and PCA9538
	
	Parameters
	----------
	i2c		: I2C instance
	address	: int, option
	
	Returns
	-------
	PCA9554 object
	
	"""
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
