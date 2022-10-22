"""
Serial interface management library for MicroPython
Akifumi (Tedd) OKANO / Released under the MIT license

version	0.2 (10-Oct-2022)
version	0.1 (01-Oct-2022)
"""
class Interface:
#	@classmethod
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

	def dump( self ):
		"""
		dump register values
	
		Returns
		-------
		list : register data
			List of integers

		"""
		return self.read_registers( 0, len( self.REG_NAME ) )

	def dump_reg( self ):
		"""
		showing all register name, address/pointer and value
		"""
		rv		= self.dump()
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

	def info( self ):
		return "an instance of {}, {}".format( self.__class__.__name__, self.dev_access() )
	
	def dev_access( self ):
		if hasattr( self, "__adr" ):
			return "target address 0x{:02X} (0x{:02X})".format( self.__adr, self.__adr << 1 )
		elif hasattr( self, "__cs" ):
			return "cs_pin@{}".format( self.__cs )

class I2C_target_Error( Exception ):
	pass

class I2C_target( Interface ):
	"""
	An abstraction class to provide I2C device access.
	It helps to keep target address and communication.
	
	For register access methods, the register can be specified
	by its name. The name of registers may needed to be defined
	as REG_NAME in inherited class (device class).
	
	"""

	def __init__( self, i2c, address, auto_increment_flag = 0x00, ignore_fail = True ):
		"""
		I2C_target initializer
	
		Parameters
		----------
		i2c : machine.I2C instance
		address : I2C target (device) address
		
		"""
		self.__adr	= address
		self.__if	= i2c
		self.__ai	= auto_increment_flag

		self.ignore_fail	= ignore_fail
		self.live			= True

	def ping( self ):
		self.live	= True
		self.send( [] )

	def send( self, tsfr, stop = True, retry = 3 ):
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
		
		if not self.live:
			return
			
		retry_setting	= retry

		while retry:
			err	= False
			try:
				self.__if.writeto( self.__adr, bytearray( tsfr ), stop )
			except Exception as e:
				err		 = True
				retry	-= 1
			else:
				retry	= 0
			
		if ( err ):
			if self.ignore_fail:
				print( "I2C error: NACK returned {} times from {}, address 0x{:02X} (0x{:02X})".format( retry_setting, self.__class__.__name__, self.__adr, self.__adr << 1 ) )
				self.live	= False
			else:
				raise I2C_target_Error( "I2C error: NACK returned {} times from {}, address 0x{:02X} (0x{:02X})".format( retry_setting, self.__class__.__name__, self.__adr, self.__adr << 1 ) )

	def receive( self, length, retry = 3 ):
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
		if not self.live:
			return
			
		retry_setting	= retry

		while retry:
			err	= False
			try:
				rtn	= list( self.__if.readfrom( self.__adr, length ) )
			except Exception as e:
				err		 = True
				retry	-= 1
			else:
				retry	= 0
			
		if ( err ):
			if self.ignore_fail:
				print( "I2C error: NACK returned {} times from {}, address 0x{:02X} (0x{:02X})".format( retry_setting, self.__class__.__name__, self.__adr, self.__adr << 1 ) )
				self.live	= False
				rtn			= None
			else:
				raise I2C_target_Error( "I2C error: NACK returned {} times from {}, address 0x{:02X} (0x{:02X})".format( retry_setting, self.__class__.__name__, self.__adr, self.__adr << 1 ) )

		return rtn

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
		#print( "I2C write_registers: {}, {}".format( reg, data ) )
		
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
		#print( "I2C read_registers: {}, {}".format( reg, data ) )

		reg	= self.REG_NAME.index( reg ) if type( reg ) != int else reg
		reg	   |= self.__ai
		self.send( [ reg ], stop = not repeated_start )
		r	= self.receive( length )
		
		return	r[ 0 ] if length is 1 else r

class SPI_target( Interface ):
	def __init__( self, spi, cs = None ):
		"""
		SPI_target initializer
	
		Parameters
		----------
		spi : machine.SPI instance
		cs : machine.Pin instance (Chip select output)
		
		"""
		self.__cs	= cs
		self.__if	= spi

		self.chip_select	= 1

	def send( self, data ):
		"""
		send data (generate write transaction)
	
		Parameters
		----------
		tsfr : list
			Data for sending. List of integers will be converted to
			bytearray before sending.
			
		"""
		self.chip_select	= 0
		self.__if.write( bytearray( data ) )
		self.chip_select	= 1

	def receive( self, tsfr ):
		"""
		receive data (generate write & read transaction)
	
		Parameters
		----------
		tsfr : list
			Data for sending. List of integers will be converted to
			bytearray before sending.

		Returns
		-------
		list : received data
			List of integers which was converted from bytearray.

		"""
		tsfr	= bytearray( tsfr )
		self.chip_select	= 0
		self.__if.write_readinto( tsfr, tsfr )
		self.chip_select	= 1
		
		return list( tsfr )

	@property
	def chip_select( self ):
		pass

	@chip_select.setter
	def chip_select( self, v ):
		if self.__cs:
			self.__cs.value( v )

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
		#print( "SPI write_registers: {}, {}".format( reg, data ) )
		
		reg		= self.REG_NAME.index( reg ) if type( reg ) != int else reg
		data	= [ reg, data ] if type(data) == int else [ reg ] + data

		self.send( data )
		
	def read_registers( self, reg, length ):
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
		#print( "SPI read_registers: {}, {}".format( reg, length ) )
		
		reg		 = self.REG_NAME.index( reg ) if type( reg ) != int else reg
		data	 = [reg | 0x80 ] + [ 0x00 ] * length

		r	= self.receive( data )

		return r[ 1 ] if 1 == length else r[ 1: ]

class abstract_target( Interface ):
	"""
	An abstraction class for off-line test.
	"""

	def send( self, tsfr ):
		print( "send: ", tsfr )

	def receive( self, length ):
		print( "receive: ", length )
		return 0

	def write_registers( self, reg, data ):
		reg		= self.REG_NAME.index( reg ) if type( reg ) != int else reg
		data	= [ reg, data ] if type(data) == int else [ reg ] + data
		self.send( data )
		
	def read_registers( self, reg, length, repeated_start = True ):
		reg	= self.REG_NAME.index( reg ) if type( reg ) != int else reg
		self.send( [ reg ], stop = not repeated_start )
		r	= self.receive( length )
		
		return	r[ 0 ] if length is 1 else r

