from	machine	import	Pin, I2C, SPI
from	utime	import	sleep

from	nxp_periph	import	SC18IS606

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
		
from	nxp_periph	import	SPI_target

class AT25010( AT25010_operation, SPI_target ):
	def __init__( self, spi, cs = None ):
		super().__init__( spi, cs )

if __name__ == "__main__":
	main()
