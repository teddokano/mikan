from	machine	import	Pin, I2C, SPI
from	utime	import	sleep

from	nxp_periph	import	I2C_target, SPI_target


class SC16IS7xx_base():
	"""
	A base class to abstract behavior of SC16IS7xx. 
	
	This makes SC16IS7xx behavior independent from interface. 	
	"""

	REG_DICT	= {
					"RHR" : 0x00, "THR" : 0x00, "IER" : 0x01, "FCR" : 0x02, 
					"IIR" : 0x02, "LCR" : 0x03, "MCR" : 0x04, "LSR" : 0x05,
					"MSR" : 0x06, "SPR" : 0x07, "TCR" : 0x06, "TLR" : 0x07,
					"TXLVL"   : 0x08, "RXLVL"    : 0x09, "IODir"     : 0x0A,
					"IOState" : 0x0B, "IOIntEna" : 0x0C, "IOControl" : 0x0E,
					"EFCR"    : 0x0F, "DLL"      : 0x00, "DLH"       : 0x01,
					"EFR"     : 0x02, "XON1"     : 0x04, "XON2"      : 0x05,
					"XOFF1"   : 0x06, "XOFF2"    : 0x07
					}

	def __init__( self, channel = 0, osc = 14746500, baud = 9600, bits = 8, parity = None, stop = 1 ):
		"""
		A base class to abstract behavior of SC16IS7xx
		
		Parameters
		----------
		channel : int, default 0
			UART channel mumber. 1 can be used for SC16IS752 and SC16IS762
		osc     : int, default 14746500
			X-tal frequency
		baud    : int, default 9600
			Baudrate setting
		bits    : int, default 8
			UART word length setting. 5, 6, 7 or 8 can be used
		parity  : int or None, default None
			None for no parity
			0 for odd, 1 for even parity
		stop    : int, default 1
			Stop bit setting. 1 or 2

		"""
		self.osc	= osc
		self.ch		= channel
		self.baud( baud )

		if parity is None:
			parity	= 0
		elif parity is 0:
			parity	= 1
		else:
			parity	= 3

		parity	<<= 3
		stop	= ((stop - 1) << 2) & 0x04
		bits	=  (bits - 5) & 0x03
		
		#	For basic operationa, see AN10462
		#	https://www.nxp.com/docs/en/application-note/AN10462.pdf
		
		self.reg_access( "LCR", 0xBF )	# access EFR register
		self.reg_access( "EFR", 0x10 )	# enable enhanced functions

		self.reg_access( "LCR", parity | stop | bits )

		self.reg_access( "FCR", 0x06 )	# reset TXFIFO, reset RXFIFO, non FIFO mode
		self.reg_access( "FCR", 0x01 )	# enable FIFO mode
		
	def info( self ):
		"""
		Not overriding interface.info() since inheritance structure can not allow
		This methos is called by SC16IS7xx_I2C and SC16IS7xx_SPI classes
		"""
		parity_setting	= [ "None", "odd", "", "even" ]
		
		s	 = "\nosc = {} Hz".format( self.osc )
		
		lcr	= self.reg_access( "LCR" )
		self.reg_access( "LCR", 0x80 )	# 0x80 to program baud rate
		s	+= ", baud = {}".format( self.osc / (((self.reg_access( "DLH" ) << 8) |  self.reg_access( "DLL" )) * 16) )						
		self.reg_access( "LCR", lcr )

		s	+= ", bits = {}".format( (lcr & 0x03) + 5 )
		s	+= ", parity = {}".format( parity_setting[ (lcr & 0x38) >> 3 ]  )
		s	+= ", stop = {}".format( ((lcr & 0x04) >> 2) + 1 )
		return s
		
	def baud( self, baud ):
		"""
		baudrate setting
	
		Parameters
		----------
		baud : int
			baudrate

		"""
		lcr	= self.reg_access( "LCR" )
		divisor	= int( self.osc / (baud * 16) )

		self.reg_access( "LCR", 0x80 )	# 0x80 to program baud rate
		self.reg_access( "DLL", divisor & 0xFF )
		self.reg_access( "DLH", divisor >> 8 )
		
		self.reg_access( "LCR", lcr )
		
	def sendbreak( self, duration = 0.1 ):
		"""
		sends break: keeps TX signal LOW for specified duration
	
		Parameters
		----------
			duration : float
				keeps TX signal LOW for given second

		"""
		lcr	= self.reg_access( "LCR" )
		self.reg_access( "LCR", 0x40 | lcr )
		sleep( duration )		
		self.reg_access( "LCR", ~0x40 & lcr )
	
	def reg_access( self, *args ):
		"""
		register access interface
		
		SC16IS7xx is not having register structure like LED controllers (PCA995x).
		Use this method to access the registers. 
	
		This method can take two arguments. 
		1st argument is a register address or name.
		2nd argument can be a value for register writing.
		If no 2nd argument given, the method returns register read value. 
	
		Parameters
		----------
		args[0] : int or string
			register address of name
		args[1] : int, option
			method returns this 2nd argument is not available
			
		Returns
		-------
		int, if 2nd argument is not exist
			register value
		
		Examples
		--------
		>>> self.reg_access( "LCR", 0x80 )	# writing
		>>> lcr	= self.reg_access( "LCR" )	# reading
		
		"""

		n_args	= len( args )
		reg		= args[ 0 ] if type( args[ 0 ] ) is int else self.REG_DICT[ args[ 0 ] ]
		
		if n_args is 1:
			return self.read_registers( (reg << 3 | self.ch), 1 )
		elif n_args is 2:
			self.write_registers( (reg << 3 | self.ch), args[ 1 ] )
		else:
			print( "reg_access error" )

	def thr_ready( self ):
		"""
		retruns True when THR register is ready to be written
		"""		
		return self.reg_access( "LSR" ) & 0x20

	def wait_tx_ready( self ):
		"""
		wait until THR register is ready to be written
		"""		
		while not self.thr_ready():
			pass

	def write( self, data ):
		"""
		data to be sent on TX
		
		Parameters
		----------
		data : int or list
			data on TX
		
		"""
		if isinstance( data, int ):
			data	= [ data ]
		elif isinstance( data, str ):
			data	= list( data )
			data	= [ ord( i ) for i in data ]
		
		for d in data:
			self.wait_tx_ready()		
			self.reg_access( "THR", d )

	def any( self ):
		"""
		returns True if received data available
		"""
		return self.reg_access( "LSR" ) & 0x01

	def flush( self ):
		"""
		wait all data in TX buffer to be sent
		"""
		while not self.reg_access( "LSR" ) & 0x40:
			pass

	def read( self, *args ):
		"""
		get received data
		
		This method can take single argument to specify length of receiving data
		
		Parameters
		----------
		args[0] : int, option
			length of receiving data
			
		Returns
		-------
		list
			received data
			
		"""
		data	= []
		n		= -1 if len( args ) is 0 else args[ 0 ]
		
		while self.any() and n:
			data	+= [ self.reg_access( "RHR" ) ]
			n		-= 1
		
		return data

class SC16IS7xx_I2C( SC16IS7xx_base, I2C_target ):
	"""
	SC16IS7xx class with I2C interface
	"""
	def __init__( self, interface, address, cs = 0, channel = 0, osc = 14746500, baud = 9600, bits = 8, parity = None, stop = 1  ):
		"""
		Initializer to be called from "SC16IS7xx()" function
		"""
		I2C_target.__init__( self, interface, address )
		SC16IS7xx_base.__init__( self, channel = channel, osc = osc, baud = baud, bits = bits, parity = parity, stop = stop )

	def info( self ):
		s	 = I2C_target.info( self )
		s	+= SC16IS7xx_base.info( self )

		return s
		
class SC16IS7xx_SPI( SC16IS7xx_base, SPI_target ):
	"""
	SC16IS7xx class with SPI interface
	"""
	def __init__( self, interface, cs = 0, channel = 0, osc = 14746500, baud = 9600, bits = 8, parity = None, stop = 1 ):
		"""
		Initializer to be called from "SC16IS7xx()" function
		"""
		SPI_target.__init__( self, interface, cs )
		SC16IS7xx_base.__init__( self, channel = channel, osc = osc, baud = baud, bits = bits, parity = parity, stop = stop )

	def info( self ):
		s	 = SPI_target.info( self )
		s	+= SC16IS7xx_base.info( self )
		
		return s

	def read_registers( self, reg, n ):
		"""
		Overriding interface.read_registers() for device specific access method
		"""
		return self.receive( [ 0x80 | reg, 0xFF ] )[ 1 ]
		
	def write_registers( self, reg, v ):
		"""
		Overriding interface.read_registers() for device specific access method
		"""
		self.send( [ reg, v ] )

DEFAULT_ADDR	= (0x90 >> 1)
DEFAULT_CS		= None

def SC16IS7xx( interface, address = DEFAULT_ADDR, cs = DEFAULT_CS, channel = 0, osc = 14746500, baud = 9600, bits = 8, parity = None, stop = 1 ):
	"""
	A constructor interface for SC16IS7xx

	Parameters
	----------
	interface	: machine.I2C or machine.SPI object
	address		: int, option
		If need to specify (for I2C interface)
	cs			: machine.Pin object
		If need to specify (for SPI interface)
	channel : int, default 0
		UART channel mumber. 1 can be used for SC16IS752 and SC16IS762
	osc     : int, default 14746500
		X-tal frequency
	baud    : int, default 9600
		Baudrate setting
	bits    : int, default 8
		UART word length setting. 5, 6, 7 or 8 can be used
	parity  : int or None, default None
		None for no parity
		0 for odd, 1 for even parity
	stop    : int, default 1
		Stop bit setting. 1 or 2

	Returns
	-------
	SC16IS7xx_I2C or SC16IS7xx_SPI object
		returns SC16IS7xx_I2C when interface == I2C
		returns SC16IS7xx_SPI when interface == SPI

	"""
	if isinstance( interface, I2C ):
		return SC16IS7xx_I2C( interface, address, channel = channel, osc = osc, baud = baud, bits = bits, parity = parity, stop = stop )

	if isinstance( interface, SPI ):
		return SC16IS7xx_SPI( interface, cs, channel = channel, osc = osc, baud = baud, bits = bits, parity = parity, stop = stop )

class SC18IS606( I2C_target ):
	"""
	SC18IS606 class
	
	The instance of SC18IS606 class will be machine.SPI compatible object.
	
	Examples
    --------
	When an AT25010 is connected to an SPI...
		>>> spi		= SPI( 0, 1000 * 1000, cs = 0 )
		>>> eeprom	= AT25010( spi )
	When an AT25010 is connected through SC18IS606...
		>>> i2c		= I2C( 0, 400 * 1000 )
		>>> bridge	= SC18IS606( i2c, 1, int = Pin( "D2", Pin.IN, Pin.PULL_UP ) )
		>>> eeprom	= AT25010( bridge )		# Give SC18IS606 instance as an SPI

	"""
	DEFAULT_ADDRESS	= 0x28

	FuncID_SPI_read_and_write		= 0x00
	FuncID_Configure_SPI_Interface	= 0xF0
	FuncID_Clear_Interrupt			= 0xF1
	FuncID_Idle_mode				= 0xF2
	FuncID_GPIO_Write				= 0xF3
	FuncID_GPIO_Read				= 0xF4
	FuncID_GPIO_Enable				= 0xF5
	FuncID_GPIO_Configuration		= 0xF6
	FuncID_Read_Version				= 0xFE
	
	MSB	= SPI.MSB
	LSB	= SPI.LSB

	def __init__( self, i2c, csn, address = DEFAULT_ADDRESS, int = None, baudrate = 1875000, polarity = 0, phase = 0, firstbit = SPI.MSB ):
		"""
		Initializer for SC18IS606

		Parameters
		----------
		i2c	: machine.I2C
		csn	: int
			ChipSelect to be used on SPI bus
		address	: int, default SC18IS606.DEFAULT_ADDRESS
			I2C target address
		int : machine.Pin
			Pin instance for interrupt input
		baudrate : int
			SCLK frequency in Hz
		polarity : int
			0 or 1. 0 for SCLK LOW while idle. 1 for SCLK HIGH while idle. 
		phase : int
			0 or 1. 0 for SCLK LOW while idle. 1 for SCLK HIGH while idle. 
		firstbit : constant
			SPI.MSB for MSB first or SPI.LSB for LSB first. 

		"""		
		if int is None:
			raise SC18IS606_Error( "SC18IS606 instance must have interrupt pin" )
			
		super().__init__( i2c, address )
		self.__int	= int
		self.__csn	= csn
		self.__flag	= False

		self.init( baudrate = baudrate, polarity = polarity, phase = phase, firstbit = firstbit )
		
		self.__clear_int()
		self.__int.irq( trigger = Pin.IRQ_FALLING, handler = self.__callback )

		
	def __callback( self, pin ):	#	interrupt handler
		"""
		interrupt handler (instance internal use)
		"""
		self.__flag	= True

	def __wait_tsfr_done( self, read_wait = False ):
		"""
		wait for transfer completed
		"""
		while self.__flag	== False:
			pass
	
		self.__flag	= False
		
		if read_wait == False:
			self.__clear_int()
		
	def __clear_int( self ):
		"""
		interrupt clear
		"""
		self.command( [ SC18IS606.FuncID_Clear_Interrupt ] )
	
	def command( self, data ):
		"""
		command to SC18IS606
		
		Parameters
		----------
		data : list
			Sends data to SC18IS606

		"""
		super().send( data )

	def send( self, data ):
		"""
		send data on SPI and return when completed (blocking transfer)
		
		Parameters
		----------
		data : list
			send data on SPI

		"""
		self.command( [ SC18IS606.FuncID_SPI_read_and_write | 0x01 << self.__csn ] + data )
		self.__wait_tsfr_done()
		
	def receive( self, data ):
		"""
		send/receive on SPI and return data when completed (blocking transfer)
		
		Parameters
		----------
		data : list
			send data on SPI

		Returns
		-------
		list
			received data
		
		"""
		self.command( [ SC18IS606.FuncID_SPI_read_and_write | 0x01 << self.__csn ] + data )
		self.__wait_tsfr_done( read_wait = True )
		return super().receive( len( data ) )

	def init( self, baudrate = 1875000, polarity = 0, phase = 0, firstbit = SPI.MSB ):
		"""
		setting SPI parameters
		"""
		FREQ	= [ 58000, 115000, 455000, 1875000 ]
		
		order	= 0 if firstbit is SPI.MSB else 1
		
		for f_idx, freq in enumerate( FREQ ):
			if baudrate <= freq:
				break
		
		self.config	= { "oeder"		: "{} first".format( "LSB" if order else "MSB" ), 
						"polarity"	: "SPICLK {} when idle".format( "HIGH" if polarity else "LOW" ), 
						"phase"		: "{} edge for data latched".format( "2nd" if phase else "1st" ),
						"freq"		: FREQ[ f_idx ]
						}

		f_idx	= 3 - f_idx		
		self.command( [ SC18IS606.FuncID_Configure_SPI_Interface ] 
							+ [ (order << 5) | (polarity << 3) | (phase << 2) | f_idx ] )
		
	def info( self ):
		"""
		overrides interface.info() for additional information
		"""
		return super().info() + "\n" + "{}Hz, {}, {}, {}".format( self.config[ "freq" ], self.config[ "oeder" ], self.config[ "polarity" ], self.config[ "phase" ] )

	def read( self, nbytes, write = 0x00 ):
		"""
		machine.SPI.read() compatible
		"""
		return self.receive( [ write ] * nbytes )

	def readinto( self, buf, write = 0x00 ):
		"""
		machine.SPI.readinto() compatible
		"""
		buf	= self.read( len( buf ), write = write )
		for i, m in enumerate( self.receive( list( write_buf ) ) ):
			buf[ i ]	= m

	def write( self, buf ):
		"""
		machine.SPI.write() compatible
		"""
		self.send( list( buf ) )

	def write_readinto( self, write_buf, read_buf ):
		"""
		machine.SPI.write_readinto() compatible
		"""
		for i, m in enumerate( self.receive( list( write_buf ) ) ):
			read_buf[ i ]	= m

class SC18IS606_Error( Exception ):
	pass
