"""
Temperature sensor operation library for MicroPython
Akifumi (Tedd) OKANO / Released under the MIT license

version	0.1 (25-Sep-2022)
"""
from nxp_periph.I2C_interface	import	I2C_target

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
		
		If 2 argument is geven, it performs write.
		If only 1 argument is geven, read is performed.

		Parameters
		----------
		args[0] : string or int
			Register name or pointer to the register.
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
			print( args[0], data )
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


class PCT2075( temp_sensor_base, I2C_target ):
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
		
