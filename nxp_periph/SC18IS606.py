from machine	import	Pin, I2C, SPI
from nxp_periph.interface	import	Interface, I2C_target, SPI_target

class SC18IS606( I2C_target ):
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
		self.__flag	= True

	def __wait_tsfr_done( self, read_wait = False ):
		while self.__flag	== False:
			pass
	
		self.__flag	= False
		
		if read_wait == False:
			self.__clear_int()
		
	def __clear_int( self ):
		self.command( [ SC18IS606.FuncID_Clear_Interrupt ] )
	
	def command( self, data ):
		super().send( data )

	def send( self, data ):
		self.command( [ SC18IS606.FuncID_SPI_read_and_write | 0x01 << self.__csn ] + data )
		self.__wait_tsfr_done()
		
	def receive( self, data ):
		self.command( [ SC18IS606.FuncID_SPI_read_and_write | 0x01 << self.__csn ] + data )
		self.__wait_tsfr_done( read_wait = True )
		return super().receive( len( data ) )

	def init( self, baudrate = 1000000, *, polarity = 0, phase = 0, firstbit = SPI.MSB ):
		FREQ	= [ 58000, 115000, 455000, 1875000 ]
		
		order	= 0 if firstbit is SPI.MSB else 1
		
		for f_idx, freq in enumerate( FREQ ):
			print( f_idx, baudrate, freq )
			if baudrate <= freq:
				break
		
		f_idx	= 3 - f_idx
		
		data	= (order << 5) | (polarity << 3) | (phase << 2) | f_idx
		print( "FuncID_Configure_SPI_Interface = 0x{:02X}".format( data ) )
		self.command( [ SC18IS606.FuncID_Configure_SPI_Interface ] + [ data ] )
		

	def read( self, nbytes, write = 0x00 ):
		return self.receive( [ write ] * nbytes )

	def readinto( self, buf, write = 0x00 ):
		buf	= self.read( len( buf ), write = write )
		for i, m in enumerate( self.receive( list( write_buf ) ) ):
			buf[ i ]	= m

	def write( self, buf ):
		self.send( list( buf ) )

	def write_readinto( self, write_buf, read_buf ):
		for i, m in enumerate( self.receive( list( write_buf ) ) ):
			read_buf[ i ]	= m

class SC18IS606_Error( Exception ):
	pass


from utime 		import	sleep

BRIDGE_DEMO	= True

def	main():
	if BRIDGE_DEMO:
		#	AT25010 access through SC18IS606 protocol bridge
		i2c		= I2C( 0, 400 * 1000 )
		bridge	= SC18IS606( i2c, 1, int = Pin( "D2", Pin.IN, Pin.PULL_UP ) )
		eeprom	= AT25010( bridge )		# Give SC18IS606 instance as an SPI
	else:
		#	AT25010 access with direct SPI connection
		spi		= SPI( 0, 1000 * 1000, cs = 0 )
		eeprom	= AT25010( spi )

	try:
		print( bridge.info() )
	except:
		print( "SPI direct connect" )
		
	print( "instance of '{}' class had been made".format( eeprom.__class__.__name__ ) )

	###
	###	Operation (EEPROM write and read)
	###

	EEPROM_ADDRESS	= 0
	DATA_LENGTH		= 8

	while True:
		data	= [ x for x in range( DATA_LENGTH ) ]
		eeprom.write_data( EEPROM_ADDRESS, data )
		eeprom.wait_write_complete()
		print( eeprom.read_data( EEPROM_ADDRESS, DATA_LENGTH ) )
		sleep( 1 )

class AT25010_operation():
	instruction_WRITE	= 0x02
	instruction_READ	= 0x03
	instruction_RDSR	= 0x05	#	read status register
	instruction_WREN	= 0x06	#	write enable
	RDSR_nRDY			= 0x01	#	nRDY bit in RDSR

	def wait_write_complete( self ):
		while self.read_status_register()[ 0 ] & AT25010.RDSR_nRDY:
			pass

	def	read_status_register( self ):
		return self.read( [ AT25010.instruction_RDSR ] + [ 0 ] )[ 1: ]

	def write( self, tsfr ):
		self.send( tsfr )
		
	def read( self, tsfr ):
		return self.receive( tsfr )
	
	def write_data( self, adr, data ):
		self.write( [ AT25010.instruction_WREN ] )
		self.write( [ AT25010.instruction_WRITE, adr ] + data )
	
	def read_data( self, adr, length ):
		return self.read( [ AT25010.instruction_READ, adr ] + [ 0 ] * length )[ 2: ]
		

class AT25010( AT25010_operation, SPI_target ):
	def __init__( self, spi, cs = None ):
		super().__init__( spi, cs )

if __name__ == "__main__":
	main()
