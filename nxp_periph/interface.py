class Interface:
	"""
	An abstraction class to provide common methods for devices
	"""
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

		if not self.live:
			return

		try:
			reg	= self.REG_NAME.index( reg ) if type( reg ) != int else reg
			rv	= self.read_registers( reg, 1 )
			wv	= rv
			
			wv	&= ~(target_bits & ~value)
			wv	|=  (target_bits &  value)

			self.write_registers( reg, wv )
		except Exception as e:
			self.live	= False
			rv, wv		= 0, 0
		
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
		"""
		device information

		Returns
		-------
		string : device information
		"""
		return "an instance of {}, {}".format( self.__class__.__name__, self.dev_access() )
	
	def dev_access( self ):
		"""
		device access information

		Returns
		-------
		string : device access information
		"""
		if hasattr( self, "__adr" ):
			return "target address 0x{:02X} (0x{:02X})".format( self.__adr, self.__adr << 1 )
		elif hasattr( self, "__cs" ):
			return "cs_pin@{}".format( self.__cs )

class I2C_target_Error( Exception ):
	"""
	Just a class for I2C exception handling
	"""
	pass

class I2C_target( Interface ):
	"""
	An abstraction class to provide I2C device access.
	It helps to keep target address and communication.
	
	For register access methods, the register can be specified
	by its name or register address/pointer. 
	The name of registers may needed to be defined as REG_NAME 
	in inherited class (device class).
	
	"""

	def __init__( self, i2c, address, auto_increment_flag = 0x00, ignore_fail = True ):
		"""
		I2C_target initializer
	
		Parameters
		----------
		i2c : obj
			machine.I2C instance
		address : int
			I2C target (device) address
		auto_increment_flag : int
			On some devices, auto increment flag is needed for consecutive 
			regiter access. This value is set in register address when 
			multiple data sending. 
		ignore_fail : bool
			Supress raising exception when transfer error (NACK) happned
			
		"""
		self.__adr	= address
		self.__if	= i2c
		self.__ai	= auto_increment_flag

		self.ignore_fail	= ignore_fail
		self.live			= True

	def ping( self ):
		"""
		ping for a device
		
		Access to the device with just its target address without data. 
		If the device returned ACK, it keeps self.live=True. If device 
		rturned NACK, the self.live is changed to False. 
	
		Returns
		-------
		bool : Returns self.live

		"""
		self.live	= True
		self.send( [] )
		
		return self.live

	def send( self, tsfr, stop = True, retry = 3 ):
		"""
		send data (generate write transaction)

		Sending list-data to the device. 
		It trys sending 3 times if the device respond NACK. 
		If the device is kept not responding, the self.live is set to 
		False to prevent further access to the failed device. 

		Forcing self.live=True can re-live the device. 
	
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

	def receive( self, length, retry = 3, barray = False ):
		"""
		receive data (generate read transaction)
	
		Receiving list-data from the device. 
		It trys receiving 3 times if the device respond NACK. 
		If the device is kept not responding, the self.live is set to 
		False to prevent further access to the failed device. 

		Forcing self.live=True can re-live the device. 
	
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
				rtn	= self.__if.readfrom( self.__adr, length )
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

		if barray:
			return rtn
		else:
			return list( rtn )

	def write_registers( self, reg, data ):
		"""
		writing registers
	
		Parameters
		----------
		reg : string or int
			Register name or register address/pointer.
		data : list or int
			Data for sending.
			List for multibyte sending. List is converted to
			bytearray before sending.
			If the data is integer, single byte will be sent.

		Examples
		--------
		self.write_registers( "PWM0", 0xFF ):		# single byte writing
		self.write_registers( "PWM0", [0xFF] * 4 ):	# 4 bytes writing
		self.write_registers( 10, [0xFF] * 4 ):		# register specified by address
			
		"""
		#print( "I2C write_registers: {}, {}".format( reg, data ) )
		
		reg		= self.REG_NAME.index( reg ) if type( reg ) != int else reg
		
		if ( type(data) == int ) or ( 1 == len( data ) ):
			pass
		else:
			reg	   |= self.__ai
		
		data	= [ reg, data ] if type(data) == int else [ reg ] + data
		self.send( data, stop = True )
		
	def read_registers( self, reg, length, repeated_start = True, barray = False  ):
		"""
		reading registers
	
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

		Examples
		--------
		data = self.read_registers( "PWM0", 1 ):	# single byte reading, returns an int
		data = self.read_registers( "PWM0", 4 ):	# 4 bytes reading, returns a list
		data = self.read_registers( 10, 4 ):		# register specified by address

		"""
		#print( "I2C read_registers: {}, {}".format( reg, data ) )

		reg	= self.REG_NAME.index( reg ) if type( reg ) != int else reg

		if length != 1:
			reg	   |= self.__ai
		
		self.send( [ reg ], stop = not repeated_start )
		r	= self.receive( length, barray = barray )
		
		return	r[ 0 ] if length is 1 else r

class SPI_target( Interface ):
	"""
	An abstraction class to provide SPI device access.
	It helps to keep target access method and communication.
	
	For register access methods, the register can be specified
	by its name or register address/pointer. 
	The name of registers may needed to be defined as REG_NAME 
	in inherited class (device class).
	
	"""

	def __init__( self, spi, cs = None ):
		"""
		SPI_target initializer
		
		Parameters
		----------
		spi : obj
			machine.SPI instance
		cs : obj
			machine.Pin instance (Chip select output)
			This 'cs' can be None in case of using hardware 
			controlledChipSelect signal
		
		"""
		self.__cs	= cs
		self.__if	= spi
		self.live	= True
		
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
		"""
		A setter method to perform CS signal HIGH/LOW by assignment
		"""
		if self.__cs:
			self.__cs.value( v )

	def write_registers( self, reg, data ):
		"""
		writing registers
	
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
		reading registers
	
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
	No physical access will be performed with this class. 
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

def i2c_fullscan( i2c ):
	"""
	I2C scan for full range of target addresses. 
	Because the machine.I2C.scan() does scan is limited in range of 0x08(0x10) 
	to 0x77(0xEE). 
	
	Parameters
	----------
	i2c : obj
		machine.I2C instance
		
	Returns
	-------
	list : Responding target ddress list

	"""

	list	= []
	data	= []
	
	for i in range( 128 ):
		try:
			i2c.writeto( i, bytearray( data ) )
		except Exception as e:
			pass
		else:
			list	+= [ i ]
			
	return list
