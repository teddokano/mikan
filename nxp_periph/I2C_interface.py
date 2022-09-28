"""
Serial interface management library for MicroPython
Akifumi (Tedd) OKANO / Released under the MIT license

version	0.1 (25-Sep-2022)
"""

class I2C_target():
	"""
	An abstraction class to provide I2C device access.
	It helps to keep target address and communication.
	
	For register access methods, the register can be specified
	by its name. The name of registers may needed to be defined
	as REG_NAME in inherited class (device class).
	
	"""

	def __init__( self, i2c, address, auto_increment_flag = 0x00 ):
		"""
		I2C_target constructor
	
		Parameters
		----------
		i2c : machine.I2C instance
		address : I2C target (device) address
		
		"""
		self.__adr	= address
		self.__i2c	= i2c
		self.__ai	= auto_increment_flag
		
	def send( self, tsfr, stop = True ):
		"""
		send data (generate write transaction)
	
		Parameters
		----------
		tsfr : list
			Data for sending. List of integers will be converted to
			bytearray before sending.
		stop : bool
			STOP-condition generated after the transaction.
			Use False to generate Repeated-START-condition on next
			transaction.
			
		"""
		self.__i2c.writeto( self.__adr, bytearray( tsfr ), stop )

	def receive( self, length ):
		"""
		receive data (generate read transaction)
	
		Parameters
		----------
		length : int
			Number of bytes for receiveing.
			
		Returns
		-------
		list : received data
			List of integers which was converted from bytearray.

		"""
		return list( self.__i2c.readfrom( self.__adr, length ) )

	def write_registers( self, reg, data ):
		"""
		writing register
	
		Parameters
		----------
		reg : string or int
			Register name or register address/pointer.
		data : list or int
			Data for sending.
			List for multibyte sending. List is converted to
			bytearray before sending.
			If the data is integer, single byte will be sent.
			
		"""
		reg		= self.REG_NAME.index( reg ) if type( reg ) != int else reg
		reg	   |= self.__ai
		data	= [ reg, data ] if type(data) == int else [ reg ] + data
		self.send( data, stop = True )
		
	def read_registers( self, reg, length, repeated_start = True ):
		"""
		reading register
	
		Parameters
		----------
		reg : string or int
			Register name or register address/pointer.
		length : int
			Number of bytes for receiveing.
		repeated_start : bool, option
			If True, a Repeated-START-condition generated between
			write and read transactions.
			If False, a STOP-condition and START-condition are
			generated between write and read transactions.

		"""
		reg	= self.REG_NAME.index( reg ) if type( reg ) != int else reg
		reg	   |= self.__ai
		self.send( [ reg ], stop = not repeated_start )
		r	= self.receive( length )
		
		return	r[ 0 ] if length is 1 else r

	def bit_operation( self, reg, target_bits, value ):
		"""
		register bit set/clear
	
		Parameters
		----------
		reg : string or int
			Register name or register address/pointer.
		target_bits : int
			select target bits by setting its bit position 1
		value : int
			set/clear value.
			The bits only set/cleared with same position at
			1 in target_bits.
			
		Returns
		-------
		int : register value before modifying
		int : register value after modifying

		"""
		reg	= self.REG_NAME.index( reg ) if type( reg ) != int else reg
		rv	= self.read_registers( reg, 1 )
		wv	= rv
		
		wv	&= ~(target_bits & ~value)
		wv	|=  (target_bits &  value)

		self.write_registers( reg, wv )
		
		return rv, wv

	def show_reg( self, reg_name ):
		"""
		showing register name, address/pointer and value

		Parameters
		----------
		reg : string
			Register name

		"""
		r	= self.REG_NAME.index( reg_name )
		rv	= self.read_registers( r, 1 )
		print( "{:16} (0x{:02X}) : 0x{:02X}".format( reg_name, r, rv ) )

	def dump_reg( self ):
		"""
		showing all register name, address/pointer and value
		"""
		length	= len( self.REG_NAME )
		rv		= self.read_registers( 0, length )

		index	= [ (i // 2) if 0 == i % 2 else (i // 2) + ((length + 1) // 2) for i in range( length ) ]
		reg		= [ self.REG_NAME[ i ] for i in index ]
		rv		= [ rv[ i ]            for i in index ]
		lf		= [ {"end":""} if 0 == i % 2 else {"end":"\n"} for i in range( length ) ]

		print( "register dump: \"{}\", I2C target address 0x{:02X} (0x{:02X})".format( self.__class__.__name__, self.__adr, self.__adr << 1 ) )
		for i, j, k, l in zip( reg, index, rv, lf ):
			print( "    {:16} (0x{:02X}) : 0x{:02X}".format( i, j, k ), **l )

		if 1 == length % 2:
			print( "" )
