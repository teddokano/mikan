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

	def config_0( self, *args ):
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
		return	[ self.read_registers( rn, 1 ) for rn in self.REG_NAME  if rn is not "reserved" ]

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

	@property
	def config( self ):
		return self.read_registers( self.__cfg, self.__np )

	@config.setter
	def config( self, v ):
		self.write_registers( self.__cfg, v )


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

class PCAL6xxx_base( GPIO_base, I2C_target ):
	def __init__( self, i2c, address, auto_increment_flag = 0x00 ):
		I2C_target.__init__( self, i2c, address, auto_increment_flag = auto_increment_flag )
		self.REG_LIST	= [ { "idx": self.REG_NAME.index( rn ), "name": rn } for rn in self.REG_NAME if rn is not "reserved" ]

	def __setup_EVB( self ):
		"""
		setting up RESET and OE pins on PCAL6408AEV-ARD evaluation board
		"""
		from machine import Pin
		from utime import sleep
		
		print( "PCAL6xxxAEV-ARD setting done." )
		rst	= Pin( "D8", Pin.OUT )
		adr	= Pin( "D9", Pin.OUT )
		rst.value( 0 )
		adr.value( self.ADDR_BIT )
		sleep( 0.01 )
		rst.value( 1 )

	@property
	def mask( self ):
		return self.read_registers( self.__im, self.__np )

	@mask.setter
	def mask( self, v ):
		self.write_registers( self.__im, v )

	@property
	def pull_en( self ):
		return self.read_registers( self.__pe, self.__np )

	@pull_en.setter
	def pull_en( self, v ):
		self.write_registers( self.__pe, v )

	@property
	def pull_up( self ):
		return self.read_registers( self.__ps, self.__np )

	@pull_up.setter
	def pull_up( self, v ):
		self.write_registers( self.__ps, v )

	@property
	def status( self ):
		return 	self.read_registers( self.__is, self.__np )

	def dump_reg( self ):
		rv		= self.dump()
		
		for i, name in enumerate( self.REG_NAME ):
			if name is "reserved":
				rv.insert( i, 0 )
		
		length	= len( rv )

		index	= [ (i // 2) if 0 == i % 2 else (i // 2) + ((length + 1) // 2) for i in range( length ) ]
		reg		= [ self.REG_NAME[ i ] for i in index ]
		rv		= [ rv[ i ]            for i in index ]
		lf		= [ {"end":""} if 0 == i % 2 else {"end":"\n"} for i in range( length ) ]

		ml		= len( max( self.REG_NAME, key = len ) )
		fmt		= "    {{:{}}}".format( ml )
		fmt	   += " (0x{:02X}) : 0x{:02X}"
		
		print( "register dump: \"{}\", {}".format( self.__class__.__name__, self.dev_access() ) )
		for i, j, k, l in zip( reg, index, rv, lf ):
			print( fmt.format( i, j, k ), **l )

		if 1 == length % 2:
			print( "" )

class PCAL65xx_base( PCAL6xxx_base ):
	AUTO_INCREMENT	= 0x80

	def __init__( self, i2c, address ):
		super().__init__( i2c, address, auto_increment_flag = self.AUTO_INCREMENT )

	def dump( self ):
		"""
		dump register values
	
		Returns
		-------
		list : register data
			List of integers

		"""
		return self.read_registers( 0, len( self.REG_LIST ) )

class PCAL6408( PCAL6xxx_base ):
	"""
	PCAL6408: 8 bit GPIO expander
	
	"""
	ADDR_BIT		= 0
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
		self.__im	= "Interrupt mask"
		self.__is	= "Interrupt status"
		self.__pe	= "Pull-up/pull-down enable"
		self.__ps	= "Pull-up/pull-down selection"
		self.__np	= self.N_PORTS

class PCAL6416( PCAL6xxx_base ):
	"""
	PCAL6416: 16 bit GPIO expander
	
	"""
	ADDR_BIT		= 0
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
		self.__im	= "Interrupt mask register 0"
		self.__is	= "Interrupt status register 0"
		self.__pe	= "Pull-up/pull-down enable register 0"
		self.__ps	= "Pull-up/pull-down selection register 0"
		self.__np	= self.N_PORTS

class PCAL6524( PCAL65xx_base ):
	"""
	PCAL6524: 24 bit GPIO expander
	
	"""
	ADDR_BIT		= 0
	DEFAULT_ADDR	= (0x44 >> 1) + ADDR_BIT
	N_PORTS			= 3
	N_BITS			= 24
	
	REG_NAME_0x00	= [ "Input Port 0", "Input Port 1", "Input Port 2", "reserved", 
						"Output Port 0", "Output Port 1", "Output Port 2", "reserved", 
						"Polarity Inversion port 0",  "Polarity Inversion port 1", "Polarity Inversion port 2", "reserved", 
						"Configuration port 0", "Configuration port 1", "Configuration port 2",
						]
	REG_NAME_0x40	= [ "Output drive strength register port 0A", "Output drive strength register port 0B", 
						"Output drive strength register port 1A", "Output drive strength register port 1B", 
						"Output drive strength register port 2A", "Output drive strength register port 2B", 
						"reserved", "reserved", 
						"Input latch register port 0", 
						"Input latch register port 1", 
						"Input latch register port 2", 
						"reserved", 
						"Pull-up/pull-down enable register port 0", 
						"Pull-up/pull-down enable register port 1", 
						"Pull-up/pull-down enable register port 2", 
						"reserved", 
						"Pull-up/pull-down selection register port 0", 
						"Pull-up/pull-down selection register port 1", 
						"Pull-up/pull-down selection register port 2", 
						"reserved", 
						"Interrupt mask register port 0", 
						"Interrupt mask register port 1", 
						"Interrupt mask register port 2", 
						"reserved", 
						"Interrupt status register port 0", 
						"Interrupt status register port 1", 
						"Interrupt status register port 2", 
						"reserved", 
						"Output port configuration register", 
						"reserved", 
						"reserved", 
						"reserved", 
						"Interrupt edge register port 0A", "Interrupt edge register port 0B", 
						"Interrupt edge register port 1A", "Interrupt edge register port 1B", 
						"Interrupt edge register port 2A", "Interrupt edge register port 2B", 
						"reserved", "reserved", 
						"Interrupt clear register port 0", 
						"Interrupt clear register port 1", 
						"Interrupt clear register port 2", 
						"reserved", 
						"Input status port 0", 
						"Input status port 1", 
						"Input status port 2", 
						"reserved", 
						"Individual pin output port 0 configuration register", 
						"Individual pin output port 1 configuration register", 
						"Individual pin output port 2 configuration register", 
						"reserved", 
						"Switch debounce enable 0", 
						"Switch debounce enable 1", 
						"Switch debounce count"
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
			
			"""
			max_clr		= Pin( "D2", Pin.OUT )
			max_oe		= Pin( "D3", Pin.OUT )
			max_ctrl_2	= Pin( "D4", Pin.OUT )
			max_ctrl_1	= Pin( "D5", Pin.OUT )
			max_ctrl_0	= Pin( "D6", Pin.OUT )

			max_clr.value( 0 )
			max_oe.value( 1 )
			max_ctrl_2.value( 0 )
			max_ctrl_1.value( 1 )
			max_ctrl_0.value( 0 )
			"""
			
		self.__in	= "Input Port 0"
		self.__out	= "Output Port 0"
		self.__pol	= "Polarity Inversion port 0"
		self.__cfg	= "Configuration port 0"
		self.__im	= "Interrupt mask register port 0"
		self.__is	= "Interrupt status register port 0"
		self.__pe	= "Pull-up/pull-down enable register port 0"
		self.__ps	= "Pull-up/pull-down selection register port 0"
		self.__np	= self.N_PORTS

class PCAL6534( PCAL65xx_base ):
	"""
	PCAL6534: 34 bit GPIO expander
	
	"""
	ADDR_BIT		= 0
	DEFAULT_ADDR	= (0x44 >> 1) + ADDR_BIT
	N_PORTS			= 5
	N_BITS			= 34

	REG_NAME_0x00	= [ "Input Port 0", "Input Port 1", "Input Port 2", "Input Port 3", "Input Port 4",
						"Output Port 0", "Output Port 1", "Output Port 2", "Output Port 3", "Output Port 4",
						"Polarity Inversion port 0",  "Polarity Inversion port 1", "Polarity Inversion port 2", "Polarity Inversion port 3", "Polarity Inversion port 4",
						"Configuration port 0", "Configuration port 1", "Configuration port 2", "Configuration port 3", "Configuration port 4", 
						]
	REG_NAME_0x30	= [ "Output drive strength register port 0A", "Output drive strength register port 0B", 
						"Output drive strength register port 1A", "Output drive strength register port 1B", 
						"Output drive strength register port 2A", "Output drive strength register port 2B", 
						"Output drive strength register port 3A", "Output drive strength register port 3B", 
						"Output drive strength register port 4A", "reserved", 
						"Input latch register port 0", 
						"Input latch register port 1", 
						"Input latch register port 2", 
						"Input latch register port 3", 
						"Input latch register port 4", 
						"Pull-up/pull-down enable register port 0", 
						"Pull-up/pull-down enable register port 1", 
						"Pull-up/pull-down enable register port 2", 
						"Pull-up/pull-down enable register port 3", 
						"Pull-up/pull-down enable register port 4", 
						"Pull-up/pull-down selection register port 0", 
						"Pull-up/pull-down selection register port 1", 
						"Pull-up/pull-down selection register port 2", 
						"Pull-up/pull-down selection register port 3", 
						"Pull-up/pull-down selection register port 4", 
						"Interrupt mask register port 0", 
						"Interrupt mask register port 1", 
						"Interrupt mask register port 2", 
						"Interrupt mask register port 3", 
						"Interrupt mask register port 4", 
						"Interrupt status register port 0", 
						"Interrupt status register port 1", 
						"Interrupt status register port 2", 
						"Interrupt status register port 3", 
						"Interrupt status register port 4", 
						"Output port configuration register", 
						"Interrupt edge register port 0A", 
						"Interrupt edge register port 0B", 
						"Interrupt edge register port 1A", 
						"Interrupt edge register port 1B", 
						"Interrupt edge register port 2A", 
						"Interrupt edge register port 2B", 
						"Interrupt edge register port 3A", 
						"Interrupt edge register port 3B", 
						"Interrupt edge register port 4A", 
						"reserved", 
						"Interrupt clear register port 0", 
						"Interrupt clear register port 1", 
						"Interrupt clear register port 2", 
						"Interrupt clear register port 3", 
						"Interrupt clear register port 4", 
						"Input status port 0", 
						"Input status port 1", 
						"Input status port 2", 
						"Input status port 3", 
						"Input status port 4", 
						"Individual pin output port 0 configuration register", 
						"Individual pin output port 1 configuration register", 
						"Individual pin output port 2 configuration register", 
						"Individual pin output port 3 configuration register", 
						"Individual pin output port 4 configuration register", 
						"Switch debounce enable 0", 
						"Switch debounce enable 1", 
						"Switch debounce count"
						]
	REG_NAME	= REG_NAME_0x00 + [ "reserved" ] * (0x30 - len( REG_NAME_0x00 )) + REG_NAME_0x30

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
			
			max_clr		= Pin( "D2", Pin.OUT )
			max_oe		= Pin( "D3", Pin.OUT )
			max_ctrl_2	= Pin( "D4", Pin.OUT )
			max_ctrl_1	= Pin( "D5", Pin.OUT )
			max_ctrl_0	= Pin( "D6", Pin.OUT )

			max_clr.value( 0 )
			max_oe.value( 1 )
			max_ctrl_2.value( 0 )
			max_ctrl_1.value( 1 )
			max_ctrl_0.value( 0 )

		self.__in	= "Input Port 0"
		self.__out	= "Output Port 0"
		self.__pol	= "Polarity Inversion port 0"
		self.__cfg	= "Configuration port 0"
		self.__im	= "Interrupt mask register port 0"
		self.__is	= "Interrupt status register port 0"
		self.__pe	= "Pull-up/pull-down enable register port 0"
		self.__ps	= "Pull-up/pull-down selection register port 0"
		self.__np	= self.N_PORTS

from	machine		import	Pin, I2C, Timer
#from	nxp_periph	import	PCAL6416, PCAL6408
import	utime

def main():
	int_flag	= False
	tim_flag	= False

	def callback( pin_obj ):
		nonlocal	int_flag
		int_flag	= True
		
	def tim_cb( tim_obj ):
		nonlocal	tim_flag
		tim_flag	= True
		
	int_pin	= Pin( "D10", Pin.IN )
	int_pin.irq( trigger = Pin.IRQ_FALLING, handler = callback )

	i2c		= I2C( 0, freq = (400 * 1000) )

	print( [ hex( v ) for v in i2c.scan() ] )

#	gpio	= PCAL6408( i2c, setup_EVB = True )
	gpio	= PCAL6416( i2c, 0x20, setup_EVB = True )
#	gpio	= PCAL6524( i2c, setup_EVB = True )
#	gpio	= PCAL6534( i2c, setup_EVB = True )
#	gpio	= PCA9554( i2c, 0x20 )

	gpio.dump_reg()

	if gpio.N_PORTS is 1:
		io_config_and_pull_up	= 0xF0
		int_mask_config			= ~io_config_and_pull_up
	elif gpio.N_PORTS is 2:
		io_config_and_pull_up	= [ 0x00, 0xFF ]
		int_mask_config			= [ 0xFF, 0x00 ]
	elif gpio.N_PORTS is 3:
		io_config_and_pull_up	= [ 0x00, 0x00, 0xF0 ]
		int_mask_config			= [ 0xFF, 0xFF, 0x0F ]
	elif gpio.N_PORTS is 5:
		io_config_and_pull_up	= [ 0x00, 0x00, 0x00, 0xE0, 0x03 ]
		int_mask_config			= [ 0xFF, 0xFF, 0xFF, 0x1F, 0xFC ]

	gpio.config		= io_config_and_pull_up
	gpio.pull_up	= io_config_and_pull_up
	gpio.mask		= int_mask_config
	gpio.pull_en	= [ 0xFF ] * gpio.__np

	tim0 = Timer(0)
	tim0.init( period= 10, callback = tim_cb)

	count	= 0

	while True:
		"""
		if int_flag:
			int_flag	= False
			status		= gpio.status
			value		= gpio.value
			print( "\n--- inetrupt:" )
			
			if type( status ) == int:
				print( "  Interrupt status = 0b{:08b}".format( status ) )
				print( "  Input Port       = 0b{:08b}".format( value  ) )
			else:
				print( "  Interrupt status = {}".format(  [ "0b{:08b}".format( i ) for i in status ]  ) )
				print( "  Input Port       = {}".format(  [ "0b{:08b}".format( i ) for i in value ]   ) )
		"""
		if tim_flag:
			tim_flag	= False

			if (gpio.N_PORTS is 5) or (gpio.N_PORTS is 3):
				gpio.write_registers( "Output Port 0", count )
				gpio.write_registers( "Output Port 1", count )
				gpio.write_registers( "Output Port 2", count )
			else:
				gpio.value	= count
			count		= (count + 1) & 0xFF
			
			r	= gpio.value

			if type( r ) == int:
				print( "port read = 0b{:08b}".format( gpio.value ), end = "\r" )
			else:
				print( "port read = {}".format( [ "0b{:08b}".format( i ) for i in r ] ), end = "\r" )
				

if __name__ == "__main__":
	main()


