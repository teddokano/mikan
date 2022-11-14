from nxp_periph.interface	import	I2C_target

def main():
	from	machine		import	Pin, I2C
	from utime import sleep
	i2c			= I2C( 0, freq = (400 * 1000) )
	temp_sensor	= PCT2075( i2c, setup_EVB = True )
	temp_sensor	= P3T1085( i2c )
	print( temp_sensor.info() )

	temp_sensor.heater	= 0

	count=0
	while True:
		value	= temp_sensor.temp
		print( "%f, heater:%s" % ( value, "ON" if temp_sensor.heater else "OFF" ) )

		temp_sensor.heater = (count // 20) & 0x1
		count	+= 1

		sleep( 1 )


class temp_sensor_base():
	"""
	An abstraction class to make user interface.
	"""

	def read( self ):
		"""
		Read temperature
	
		Returns
		-------
		float : temperature in degree-Celsius
			
		"""
		return self.__read()

	def reg_access( self, *args ):
		"""
		Write or read register
		
		Takes 1 or 2 arguments.
		If 2 arguments are geven, it performs write.
		If only 1 argument is geven, read is performed.

		Parameters
		----------
		args[0] : string or int
			Register name or pointer.
		args[1] : int, optional
			Data to be written.
			
		Returns
		-------
		int : register data
			Nothing will be returned when write is done.

		"""
		length	= self.REG_ACC[ args[ 0 ] ]

		if 2 == len( args ):
			data	= [ args[ 1 ] >> 8, args[ 1 ] & 0x00FF ] if 2 == length else args[ 1 ]
			#print( args[0], data )
			self.write_registers( args[ 0 ], data )
		else:
			data	= self.read_registers( args[ 0 ], length )
			if 2 == length:
				data	= data[ 0 ] << 8 | data[ 1 ]
			
			return data
	
	def temp_setting( self, lst ):
		"""
		Over-temperature threshold and hysterisis setting
		
		Parameters
		----------
		lst : list of 2 float numbers
			Values are given in degree-Celsius.
			Bigger value will be the Over-temperature threshold
			and smaller value will be the hysterisis.
			
		Returns
		-------
		list : list of 2 float numbers
			Actual values set in the device in order of
			[ hysterisis, over_temp_threshold ] .

		"""

		return self.__value_setting( lst )
		
	def dump_reg( self ):
		"""
		Showing all register name, address/pointer and value
		(Overriding I2C_target class method)
		"""
		data	= [ self.reg_access( k ) for k in self.REG_NAME ]
		fmt		= ( "", "{:02X}", "{:04X}" )
		
		print( "register dump: \"{}\", I2C target address 0x{:02X} (0x{:02X})".format( self.__class__.__name__, self.__adr, self.__adr << 1 ) )
		for k, i, v in zip( self.REG_NAME, range( len( self.REG_NAME ) ), data ):
			print( ("    {:6} (0x{:02X}) : 0x" + fmt[ self.REG_ACC[ k ] ]).format( k, i, v ) )

	def dump( self ):
		data	= [ self.reg_access( k ) for k in self.REG_NAME ]
		return data

	@property
	def temp( self ):
		"""
		Read temperature
	
		Returns
		-------
		float : temperature in degree-Celsius
			
		"""
		return self.__read()

class LM75B( temp_sensor_base, I2C_target ):
	DEFAULT_ADDR		= 0x90 >> 1

	REG_NAME	= ( "Temp", "Conf", "Thyst", "Tos", "Tidle" )
	REG_LEN		= (      2,      1,       2,     2,       1 )
	REG_ACC		= dict( zip( REG_NAME, REG_LEN ) )

	def __init__( self, i2c, address = DEFAULT_ADDR ):
		super().__init__( i2c, address )

	def __read( self ):
		temp	= self.reg_access( "Temp" )
		return (temp & 0xFFE0) / 256.0

	def __value_setting( self, lst ):
		lst.sort()
	
		sv	= []
		for r, v in zip( ( "Thyst", "Tos" ), lst ):
			v	= int(v * 256.0) & 0xFF80
			self.reg_access( r, v )
			sv	+= [ v ]
		
		return [ v / 256.0 for v in sv ]
		
class PCT2075( LM75B ):
	DEFAULT_ADDR		= 0x90 >> 1

	REG_NAME	= ( "Temp", "Conf", "Thyst", "Tos", "Tidle" )
	REG_LEN		= (      2,      1,       2,     2,       1 )
	REG_ACC		= dict( zip( REG_NAME, REG_LEN ) )
	
	def __init__( self, i2c, address = DEFAULT_ADDR, setup_EVB = False ):
		super().__init__( i2c, address )

		if setup_EVB:
			self.heater_state	= False

			from machine import Pin
			#self.int_pin	= Pin( "D2", Pin.IN  )
			self.heater_pin	= Pin( "D3", Pin.OUT )	#	R19 as heater
	
	@property
	def heater( self ):
		return self.heater_state

	@heater.setter
	def heater( self, v ):
		self.heater_state	= v
		self.heater_pin( v )


class P3T1085( LM75B ):
	"""
	CAUTION: THIS DEVICE HAS NOT BEEN SUPPORTED YET
	"""
	DEFAULT_ADDR		= 0x90 >> 1

	REG_NAME	= ( "Temp", "Conf", "T_LOW", "T_HOGH" )
	REG_LEN		= (      2,      2,       2,        2 )
	REG_ACC		= dict( zip( REG_NAME, REG_LEN ) )

	def __init__( self, i2c, address = DEFAULT_ADDR, setup_EVB = False ):
		super().__init__( i2c, address )

		if setup_EVB:
			self.heater_state	= False

			from machine import Pin
			self.alert	= Pin( "D8", Pin.IN  )

	def __read( self ):
		temp	= self.reg_access( "Temp" )
		return (temp & 0xFFF0) / 256.0

	def __value_setting( self, lst ):
		lst.sort()
	
		sv	= []
		for r, v in zip( ( "T_LOW", "T_HOGH" ), lst ):
			v	= int(v * 256.0) & 0xFFF0
			self.reg_access( r, v )
			sv	+= [ v ]
		
		return [ v / 256.0 for v in sv ]

	@property
	def alert( self ):
		return self.alert

if __name__ == "__main__":
	main()



