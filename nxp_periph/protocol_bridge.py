from	machine	import	Pin, I2C, SoftSPI, SPI
from	utime	import	sleep

from	nxp_periph	import	I2C_target, SPI_target

class SC16IS7xx_base():
	REG_DICT	= {
					"RHR"	: 0x00,
					"THR"	: 0x00,
					"IER"	: 0x01,
					"FCR"	: 0x02,
					"IIR"	: 0x02,
					"LCR"	: 0x03,
					"MCR"	: 0x04,
					"LSR"	: 0x05,
					"MSR"	: 0x06,
					"SPR"	: 0x07,
					"TCR"	: 0x06,
					"TLR"	: 0x07,
					"TXLVL"	: 0x08,
					"RXLVL"	: 0x09,
					"IODir"	: 0x0A,
					"IOState"	: 0x0B,
					"IOIntEna"	: 0x0C,
					"IOControl"	: 0x0E,
					"EFCR"	: 0x0F,
					"DLL" 	: 0x00,
					"DLH"	: 0x01,
					"EFR"	: 0x02,
					"XON1"	: 0x04,
					"XON2"	: 0x05,
					"XOFF1"	: 0x06,
					"XOFF2"	: 0x07
					}

	def __init__( self, channel = 0, osc = 14746500, baud = 9600, bits = 8, parity = None, stop = 1 ):
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
		
		self.reg_access( "LCR", 0xBF )	# access EFR register
		self.reg_access( "EFR", 0x10 )	# enable enhanced functions

		self.reg_access( "LCR", parity | stop | bits )

		self.reg_access( "FCR", 0x06 )	# reset TXFIFO, reset RXFIFO, non FIFO mode
		self.reg_access( "FCR", 0x01 )	# enable FIFO mode
#		self.reg_access( "FCR", 0xF1 )	# enable FIFO mode

		print( "LCR:0x{:02X}".format( self.reg_access( "LCR" ) ) )
		print( "MCR:0x{:02X}".format( self.reg_access( "MCR" ) ) )
		print( "LSR:0x{:02X}".format( self.reg_access( "LSR" ) ) )

	def baud( self, baud ):
		lcr	= self.reg_access( "LCR" )
		divisor	= int( self.osc / (baud * 16) )
		print( divisor )

		self.reg_access( "LCR", 0x80 )	# 0x80 to program baud rate
		self.reg_access( "DLL", divisor & 0xFF )
		self.reg_access( "DLH", divisor >> 8 )
		
		print( divisor )

		self.reg_access( "LCR", lcr )
		
	def sendbreak( self, duration = 0.1 ):
		lcr	= self.reg_access( "LCR" )
		self.reg_access( "LCR", 0x40 | lcr )
		sleep( duration )		
		self.reg_access( "LCR", ~0x40 & lcr )
	
	def reg_access( self, *args ):
		n_args	= len( args )
		reg		= args[ 0 ] if type( args[ 0 ] ) is int else self.REG_DICT[ args[ 0 ] ]
		
		if n_args is 1:
			return self.read_registers( (reg << 3 | self.ch), 1 )
		elif n_args is 2:
			self.write_registers( (reg << 3 | self.ch), args[ 1 ] )
		else:
			print( "reg_access error" )

	def reg_access_SPI( self, *args ):
		n_args	= len( args )
		reg		= args[ 0 ] if type( args[ 0 ] ) is int else self.REG_DICT[ args[ 0 ] ]
		
		if n_args is 1:
			return self.receive( [ 0x80 | (reg << 3 | self.ch), 0xFF ] )[ 1 ]
		elif n_args is 2:
			self.send( [ (reg << 3 | self.ch), args[ 1 ] ] )
		else:
			print( "reg_access error" )

	def txdone( self ):
		return self.reg_access( "LSR" ) & 0x20

	def wait_tx_ready( self ):
		while not self.txdone():
			pass

	def write( self, data ):
		if isinstance( data, int ):
			data	= [ data ]
		elif isinstance( data, str ):
			data	= list( data )
			data	= [ ord( i ) for i in data ]
		
		for d in data:
			self.wait_tx_ready()		
			self.reg_access( "THR", d )

	def any( self ):
		return self.reg_access( "LSR" ) & 0x01

	def flush( self ):
		while not self.reg_access( "LSR" ) & 0x40:
			pass

	def read( self, *args ):
		data	= []
		n		= -1 if len( args ) is 0 else args[ 0 ]
		
		while self.any() and n:
			data	+= [ self.reg_access( "RHR" ) ]
			n		-= 1
		
		return data

class SC16IS7xx_I2C( SC16IS7xx_base, I2C_target ):
	"""
	PCF2131 class with I2C interface
	"""
	def __init__( self, interface, address, cs = 0, channel = 0, osc = 14746500, baud = 9600, bits = 8, parity = None, stop = 1  ):
		I2C_target.__init__( self, interface, address )
		SC16IS7xx_base.__init__( self, channel = channel, osc = osc, baud = baud, bits = bits, parity = parity, stop = stop )

class SC16IS7xx_SPI( SC16IS7xx_base, SPI_target ):
	"""
	PCF2131 class with SPI interface
	"""
	def __init__( self, interface, cs = 0, channel = 0, osc = 14746500, baud = 9600, bits = 8, parity = None, stop = 1 ):
		SPI_target.__init__( self, interface, cs )
		SC16IS7xx_base.__init__( self, channel = channel, osc = osc, baud = baud, bits = bits, parity = parity, stop = stop )

DEFAULT_ADDR	= (0x90 >> 1)
DEFAULT_CS		= None

def SC16IS7xx( interface, address = DEFAULT_ADDR, cs = DEFAULT_CS ):
	"""
	A constructor interface for PCF2131

	Parameters
	----------
	interface	: machine.I2C or machine.SPI object
	address		: int, option
		If need to specify (for I2C interface)
	cs			: machine.Pin object
		If need to specify (for SPI interface)

	Returns
	-------
	SC16IS7xx_I2C or SC16IS7xx_SPI object
		returns SC16IS7xx_I2C when interface == I2C
		returns SC16IS7xx_SPI when interface == SPI

	"""
	if isinstance( interface, I2C ):
		return SC16IS7xx_I2C( interface, address )

	if isinstance( interface, SPI ):
		return SC16IS7xx_SPI( interface, cs )

def main():
	intf	= I2C( 0, freq = (400 * 1000) )
	print( intf.scan() )
#	intf	= SPI( 0, 1000 * 1000, cs = 0 )
	br		= SC16IS7xx( intf )
	
	while True:
		#print( "#" )
		br.write( 0xAA )
		br.write( 0x55 )
		br.write( [ x for x in range( 8 ) ] )
		br.write( "abcdefg" )
		br.flush()
		br.sendbreak()
		if br.any():
			print( br.read() )

if __name__ == "__main__":
	main()
