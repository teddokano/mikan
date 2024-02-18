from	nxp_periph.interface	import	I2C_target, SPI_target
from	utime					import	sleep_ms

class EEPROM_base():
	"""
	An abstraction class to make user interface.
	"""

	def write( self, byte_addr, data ):
		"""
		write data
		
		Parameters
		----------
		byte_addr : int
			Start byte address for EEPROM data writing
		data : list or str
				
		Returns
		-------
		int : Written data length

		"""
		if isinstance( data, str ):
			data	= [ ord( i ) for i in data ]
			
		return self.__write( byte_addr, data )
		
	def wait_write_complete( self, times = 10 ):
		"""
		wait loop until write complete
		
		This will raise exception if write couldn;t be completed
		
		Parameters
		----------
		times : int (option)
			loop time setting
				
		Returns
		-------
		int : Written data length


		"""
		self.__wait_write_complete( times )
		
	def read( self, byte_addr, length, format = None ):
		"""
		read data
		
		Parameters
		----------
		byte_addr : int
			Start byte address for EEPROM data writing
		length : int
			Data length to read
		format : str (option)
			If format is "str", it will return data in string
					
		Returns
		-------
		int : Written data length

		"""
		data	= self.__read( byte_addr, length )
		
		if format == "str":
			data	= "".join( map( chr, data ) )
			
		return data


class EEPROM_Error( Exception ):
	"""
	Just a class for EEPROM exception handling
	"""
	pass


class M24C02( EEPROM_base, I2C_target ):
	DEFAULT_ADDR	= 0xA0 >> 1

	def __init__( self, i2c, address = DEFAULT_ADDR ):
		"""
		Initializer for M24C02
			
		Parameters
		----------
		i2c		: machine.I2C instance
		address	: int, option
			
		"""
		I2C_target.__init__( self, i2c, address )

	def __write( self, byte_addr, data ):
		page_size	= 16
		written		= 0

		length	= 1 if type(data) == int else len( data )

		self.wait_write_complete()
		
		while length:
			w_size	= page_size if page_size < length else length
			self.write_registers( byte_addr + written, data[ written : written + w_size ] )
			written	+= w_size
			length	-= w_size
			
			self.wait_write_complete()

		return written
		
	def __wait_write_complete( self, times ):
		while (not self.ping()) and times:
			times	-= 1
			sleep_ms( 1 )
		
		if not times:
			raise EEPROM_Error( "EEPROM write couldn't be complete" )
		
		return times
		
	def __read( self, byte_addr, length = None ):
		if (length is None) or (length == 1):
			return read_registers( byte_addr )
		
		page_size	= 32
		read_done	= 0
		data		= []
		
		while length:
			r_size		 = page_size if page_size < length else length
			data		+= self.read_registers( byte_addr + read_done, r_size )
			read_done	+= r_size
			length		-= r_size
			
		return data

	def __wait_write_complete( self, times = 10 ):
		while times:
			sleep_ms( 4 )
			times	-= 1
			if self.ping():
				break
		
		if not times:
			raise EEPROM_Error( "EEPROM write couldn't be completed" )
		
		return times

def test_M24C02():
	from	machine		import	I2C
	from	utime		import	sleep
	
	i2c		= I2C( 0, freq = (400 * 1000) )
	eeprom	= M24C02( i2c )
	
	print( eeprom.info() )

	test_list	= [ i for i in range( ord( 'A' ), ord( 'z' ) + 1 )]

	while True:
		eeprom.write( 0, test_list )
		read_data	= eeprom.read( 0, len( test_list ) )
		print( f'read result = "{"".join(map(chr, read_data))}"' )

		eeprom.write( 0, test_list[::-1] )
		read_data	= eeprom.read( 0, len( test_list ), format = "str" )
		print( f'read result = "{read_data}"' )
		
		sleep( 1 )


class Potentiometer_base():
	pass

class AD5161_I2C( Potentiometer_base, I2C_target ):
	DEFAULT_ADDR	= 0x5A >> 1
	
	def __init__( self, i2c, address = DEFAULT_ADDR ):
		I2C_target.__init__( self, i2c, address )
		
	def value( self, v = None ):
		if v is None:
			return self.receive( 1 )[ 0 ]
		else:
			self.write_registers( 0x00, v )

class AD5161_SPI( Potentiometer_base, SPI_target ):
	DEFAULT_ADDR	= 0x5A >> 1
	
	def __init__( self, spi, cs = None ):
		SPI_target.__init__( self, spi, cs )
				
	def value( self, v = None ):
		# 2 bytes same values are sent to read back the first written byte
		return self.receive( [ v ] )[ 0 ]


from	machine		import	I2C, SPI

DEFAULT_ADDR	= 0x5A >> 1
DEFAULT_CS		= None

def AD5161( interface, address =  DEFAULT_ADDR, cs = DEFAULT_CS ):
	"""
	A constructor interface for AD5161

	Parameters
	----------
	interface	: machine.I2C or machine.SPI object
	address		: int, option
		If need to specify (for I2C interface)
	cs			: machine.Pin object
		If need to specify (for SPI interface)

	Returns
	-------
	AD5161_I2C or AD5161_SPI object
		returns AD5161_I2C when interface == I2C
		returns AD5161_SPI when interface == SPI

	Examples
	--------
	For using I2C
		>>> intf = I2C( 0, freq = (400 * 1000) )
		>>> rtc  = AD5161( intf )
	For using SPI
		>>> intf = SPI( 0, 500 * 1000, cs = 0 )
		>>> rtc  = AD5161( intf )
	
	"""
	if isinstance( interface, I2C ):
		return AD5161_I2C( interface, address )

	if isinstance( interface, SPI ):
		return AD5161_SPI( interface, cs )

			

def test_AD5161( sel_I2C = True ):
	from	machine		import		Pin, I2C, ADC
	from	utime		import		sleep
	from	nxp_periph.MikanUtil	import	BusInOut

	"""
	"A2": SPI = 0, I2C = 1
	"A3": 0 to route op-amp output to "A1"
	"D5": 0 to Disconnect CS and set address 0x5A, 1 to connrct CS to AD5161
	"""
	setting	= BusInOut( [ "A2", "A3", "D5" ], output = True )
	ldo1	= BusInOut( [ "D4", "D1", "D0" ], output = True )
	ldo2	= BusInOut( [ "D3", "D2" ], output = True )
	alt_spi	= BusInOut( [ "D6", "D7", "D8", "D9" ] )
	adc		= ADC( Pin( "A0" ) )
	
	if sel_I2C:
		setting.v	= 0b100
		s0			= ""
		pot			= AD5161( I2C( 0, freq = (400_000) ) )
	else:
		setting.v	= 0b001
		s0			= "(previous value)"
		pot			= AD5161( SPI( 0, 1000_000, cs = 0 ) )


	v1_values = [ 1.2, 1.8, 2.5, 3.3, 0.95 ]
	v2_values = [ 1.8, 2.5, 3.3, 4.96]

	while True:
		for v1 in range( 5 ):
			ldo1.v	= v1
			for v2 in range( 4 ):
				ldo2.v	= v2
				
				print(
					"New voltages are set: LDO1 = {}V, LDO2 = {}V".format(
						v1_values[v1], v2_values[v2]
					)
				)
				sleep(1)
            
				for i in range( 0, 256, 16 ):
					if sel_I2C:
						pot.value( i )
						rb	= pot.value()
					else:
						rb	= pot.value( i )
						
					ad	= 3.3 * adc.read_u16() / 65536
					print( f"sent: {i:3}  read back{s0}: {rb:3}  output voltage: {ad:4.2f}V", end = "\r" )
					sleep( 0.01 )
	
				print( "" )
			
def main():
	#test_M24C02()
	test_AD5161( sel_I2C = False )

if __name__ == "__main__":
	main()
