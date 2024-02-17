from	nxp_periph.interface	import	I2C_target
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


class AD5161_base():
	pass

class AD5161_I2C( I2C_target ):
	DEFAULT_ADDR	= 0x5A >> 1
	
	def __init__( self, i2c, address = DEFAULT_ADDR ):
		I2C_target.__init__( self, i2c, address )
		
	def value( self, v = None ):
		if v is None:
			return self.receive( 1 )[ 0 ]
		else:
			self.write_registers( 0x00, v )
			

def test_AD5161_I2C():
	from	machine		import	Pin, I2C, ADC
	from	utime		import	sleep
	
	interface_select	= Pin( "A2", Pin.OUT )
	analogout_select	= Pin( "A3", Pin.OUT )
	interface_select.value( True )
	analogout_select.value( False )

	mux_vcca_en			= Pin( "D4", Pin.OUT )
	mux_vcca_en.value( False )
	
	i2c	= I2C( 0, freq = (400 * 1000) )
	pot	= AD5161_I2C( i2c )
	
	adc		= ADC( Pin( "A0" ) )
			
	while True:
		for i in range( 256 ):
			pot.value( i )
			print( f"{i:3}  {adc.read_u16()/65536}" )
			sleep( 0.01 )
	




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

			
def main():
	#test_M24C02()
	test_AD5161_I2C()
	
if __name__ == "__main__":
	main()
