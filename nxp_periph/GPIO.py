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

	def dump( self ):
		"""
		dump register values overriding Interface.dump()
	
		Returns
		-------
		list : register data
			List of integers

		"""
		return [ self.read_registers( i, 1 ) for i in range( len( self.REG_NAME ) ) ]


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
	
	"""
	DEFAULT_ADDR	= 0x40 >> 1
	N_PORTS			= 2
	N_BITS			= 16
	
	REG_NAME	= ( "Input port 0", "Input port 1",
					"Output port 0", "Output port 1",
					"Polarity Inversion port 0", "Polarity Inversion port 1",
					"Configuration port 0", "Configuration port 1"
					)

	def __init__( self, i2c, address = DEFAULT_ADDR ):
		"""
		Parameters
		----------
		i2c		: I2C instance
		address	: int, option
		
		"""
		super().__init__( i2c, address )
		self.__in	= "Input port 0"
		self.__out	= "Output port 0"
		self.__pol	= "Polarity Inversion port 0"
		self.__cfg	= "Configuration port 0"
		self.__np	= self.N_PORTS

class PCA9554( GPIO_base, I2C_target ):
	"""
	PCA9554: 8 bit GPIO expander
	
	A device class for an industry standard 8 bit GPIO expander
	This class can operate its family devices of
	  PCA9554A, PCA9554B, PCA954C and PCA9538
	
	"""
	DEFAULT_ADDR	= 0x40 >> 1
	N_PORTS			= 1
	N_BITS			= 8
	
	REG_NAME	= ( "Input Port",
					"Output Port"
					"Polarity Inversion",
					"Configuration"
					)

	def __init__( self, i2c, address = DEFAULT_ADDR ):
		"""			
		Parameters
		----------
		i2c		: I2C instance
		address	: int, option

		"""
		super().__init__( i2c, address )
		self.__in	= "Input Port"
		self.__out	= "Output Port"
		self.__pol	= "Polarity Inversion"
		self.__cfg	= "Configuration"
		self.__np	= self.N_PORTS

class PCAL6408( GPIO_base, I2C_target ):
	"""
	PCAL6408: 8 bit GPIO expander
	
	"""
	ADDR_BIT		= 1
	DEFAULT_ADDR	= (0x40 >> 1) + ADDR_BIT
	N_PORTS			= 1
	N_BITS			= 8
	
	REG_NAME_0x00	= [ "Input Port",
						"Output Port",
						"Polarity Inversion",
						"Configuration", 
						]
	REG_NAME_0x40	= [ "Output drive strength 0", "Output drive strength 1", 
						"Input latch", 
						"Pull-up/pull-down enable", 
						"Pull-up/pull-down selection", 
						"Interrupt mask", 
						"Interrupt status", 
						"Output port configuration", 
						]
	REG_NAME	= REG_NAME_0x00 + [ "reserved" ] * (0x40 - len( REG_NAME_0x00 )) + REG_NAME_0x40


	def __init__( self, i2c, address = DEFAULT_ADDR, setup_EVB = False ):
		"""
		Parameters
		----------
		i2c		: I2C instance
		address	: int, option

		"""
		super().__init__( i2c, address )
		
		if setup_EVB:
			self.__setup_EVB()
			
		self.__in	= "Input Port"
		self.__out	= "Output Port"
		self.__pol	= "Polarity Inversion"
		self.__cfg	= "Configuration"
		self.__np	= self.N_PORTS

	def __setup_EVB( self ):
		"""
		setting up RESET and OE pins on PCAL6408AEV-ARD evaluation board
		"""
		from machine import Pin
		from utime import sleep
		
		print( "PCAL6408AEV-ARD setting done." )
		rst	= Pin( "D8", Pin.OUT )
		adr	= Pin( "D9", Pin.OUT )
		rst.value( 0 )
		adr.value( self.ADDR_BIT )
		sleep( 0.01 )
		rst.value( 1 )

		self.write_registers( "Pull-up/pull-down enable", 0xF0 )
		self.write_registers( "Pull-up/pull-down selection", 0xFF )

class PCAL6416( GPIO_base, I2C_target ):
	"""
	PCAL6416: 16 bit GPIO expander
	
	"""
	ADDR_BIT		= 1
	DEFAULT_ADDR	= (0x40 >> 1) + ADDR_BIT
	N_PORTS			= 2
	N_BITS			= 16
	
	REG_NAME_0x00	= [ "Input Port 0", "Input Port 1",
						"Output Port 0", "Output Port 1", 
						"Polarity Inversion port 0", "Polarity Inversion port 1", 
						"Configuration port 0", "Configuration port 1", 
						]
	REG_NAME_0x40	= [ "Output drive strength register 0", "Output drive strength register 0B", 
						"Output drive strength register 1", "Output drive strength register 1B", 
						"Input latch register 0", 
						"Input latch register 1", 
						"Pull-up/pull-down enable register 0", 
						"Pull-up/pull-down enable register 1", 
						"Pull-up/pull-down selection register 0", 
						"Pull-up/pull-down selection register 1", 
						"Interrupt mask register 0", 
						"Interrupt mask register 1", 
						"Interrupt status register 0", 
						"Interrupt status register 1", 
						"Output port configuration register", 
						]
	REG_NAME	= REG_NAME_0x00 + [ "reserved" ] * (0x40 - len( REG_NAME_0x00 )) + REG_NAME_0x40


	def __init__( self, i2c, address = DEFAULT_ADDR, setup_EVB = False ):
		"""
		Parameters
		----------
		i2c		: I2C instance
		address	: int, option

		"""
		super().__init__( i2c, address )
		
		if setup_EVB:
			self.__setup_EVB()
			
		self.__in	= "Input Port 0"
		self.__out	= "Output Port 0"
		self.__pol	= "Polarity Inversion port 0"
		self.__cfg	= "Configuration port 0"
		self.__np	= self.N_PORTS

	def __setup_EVB( self ):
		"""
		setting up RESET and OE pins on PCAL6416AEV-ARD evaluation board
		"""
		from machine import Pin
		from utime import sleep
		
		print( "PCAL6416AEV-ARD setting done." )
		rst	= Pin( "D8", Pin.OUT )
		adr	= Pin( "D9", Pin.OUT )
		rst.value( 0 )
		adr.value( self.ADDR_BIT )
		sleep( 0.01 )
		rst.value( 1 )

		self.write_registers( "Pull-up/pull-down enable register 1", 0xFF )
		self.write_registers( "Pull-up/pull-down selection register 1", 0xFF )

"""
from	machine		import	I2C
from	nxp_periph	import	PCA9555
import	utime

def main():
	i2c		= I2C( 0, freq = (400 * 1000) )
	gpio	= PCAL6408( i2c, setup_EVB = True )

	print( i2c.scan() )

	gpio.dump_reg()

	#	port0 is output, port1 is input
	#	check operation by connecting port0 pin to port1 pin
#	gpio.config( [ 0x00, 0xFF ] )
	gpio.config( 0xF0 )

	while True:
		for i in range( 16 ):
#			gpio.value	= [ i, i ]
#			utime.sleep( 0.01 )

			gpio.value	= i
			utime.sleep( 0.1 )
			r	= gpio.value
			
			if type( r ) == int:
				print( "port read = {:08b}".format( r ), end = "\r" )
			else:
				print( "port read = {}".format( [ "{:08b}".format( i ) for i in r ] ), end = "\r" )


if __name__ == "__main__":
	main()
"""

