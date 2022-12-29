from nxp_periph.interface	import	I2C_target

class PCA8561( I2C_target ):
	"""
	PCA8561: LCD driver
	
	"""
	DEFAULT_ADDR	= 0x70 >> 1
	
	REG_NAME	= [ "Software_reset", 
					"Device_ctrl",
					"Display_ctrl_1",
					"Display_ctrl_2",
					"COM0_07_00",
					"COM0_15_08",
					"COM0_17_16",
					"COM1_07_00",
					"COM1_15_08",
					"COM1_17_16",
					"COM2_07_00",
					"COM2_15_08",
					"COM2_17_16",
					"COM3_07_00",
					"COM3_15_08",
					"COM3_17_16"
					]

	def __init__( self, i2c, address = DEFAULT_ADDR ):
		"""
		Initializer for PCA8561 class instance

		Parameters
		----------
		i2c		: I2C instance
		address	: int, option

		"""
		super().__init__( i2c, address )
		
		self.reg_buffer	= [ 0x00 ] * 12
		self.str_buffer	= []
	
	def com_seg( self, com, seg, v ):
		reg	= [	[ "COM0_07_00", "COM0_15_08", "COM0_17_16" ],
				[ "COM1_07_00", "COM1_15_08", "COM1_17_16" ],
				[ "COM2_07_00", "COM2_15_08", "COM2_17_16" ],
				[ "COM3_07_00", "COM3_15_08", "COM3_17_16" ]
				]
		self.bit_operation( reg[ com ][ seg // 8 ], 1 << (seg % 8), v << (seg % 8) )

	def puts( self, s, char_per_sec = 0 ):
		"""
		Print a string on LCD
		
		If the string contains more than 4 characters, 
		the last 4 characters will be shown unless char_per_sec is given. 
		
		Parameters
		----------
		s				: string
			A string to print
		char_per_sec	: float, default = 0
			Character scroll speed
			
		"""
		for c in s:
			self.putchar( c, buffer_update_only = True )
			
			if 0 < char_per_sec:
				self.flush()
				sleep( 1 / char_per_sec )
				
		if char_per_sec <= 0:
			self.flush()

	def putchar( self, c, buffer_update_only = False ):
		"""
		Print a character on LCD
		
		If the string contains more than 4 characters, 
		the last 4 characters will be shown unless char_per_sec is given. 
		
		Parameters
		----------
		c					: str
			A character to print
		buffer_update_only	: bool, default = False
			Character is not shoun in LCD. Just fills str_buffer
			
		"""
		length	= len( self.str_buffer )
		if length == 4:
			self.str_buffer	= self.str_buffer[1:] + [ c ]
		else:
			self.str_buffer += [ c ]
		
		for i, v in enumerate( self.str_buffer ):
			self.char2seg( i, v )
		
		if not buffer_update_only:
			self.flush()

	def clear( self ):
		"""
		Clear LCD
		"""
		self.reg_buffer	= [ 0x00 ] * 12
		self.str_buffer	= []
		self.flush()

	def flush( self ):
		"""
		Flash register buffer contents to LCD
		"""
		self.write_registers( "COM0_07_00", self.reg_buffer )

	def char2seg( self, pos, c ):
		"""
		Character converted to segment pattern.
		
		Generated pattern is stored in reg_buffer. 
		To show the result on the LCD, call PCA8561.flush()
		
		Parameters
		----------
		pos	: int
			Character position (0 to 3 from left)
		c	: str
			A character
		
		"""
		try:
			p	= self.CHAR_PATTERN[ c.upper() ]
		except Exception as e:
			print( "undefined character is used : \"%c\"" % c )
			p	= 0xFFFF
			
		c0	=  p        & 0x0F
		c1	= (p >>  4) & 0x0F
		c2	= (p >>  8) & 0x0F
		c3	= (p >> 12) & 0x0F			
			
		self.reg_buffer[ pos // 2 + 0 ]	&= ~(0x0F << (4 * (pos % 2)))
		self.reg_buffer[ pos // 2 + 3 ]	&= ~(0x0F << (4 * (pos % 2)))
		self.reg_buffer[ pos // 2 + 6 ]	&= ~(0x0F << (4 * (pos % 2)))
		self.reg_buffer[ pos // 2 + 9 ]	&= ~(0x0F << (4 * (pos % 2)))

		self.reg_buffer[ pos // 2 + 0 ]	|= c0 << (4 * (pos % 2))
		self.reg_buffer[ pos // 2 + 3 ]	|= c1 << (4 * (pos % 2))
		self.reg_buffer[ pos // 2 + 6 ]	|= c2 << (4 * (pos % 2))
		self.reg_buffer[ pos // 2 + 9 ]	|= c3 << (4 * (pos % 2))
	
	"""
	Character pattern for PCA8561AHN-ARD
	"""
	CHAR_PATTERN	= {
						" ": 0b_0000_0000_0000_0000,
						"A": 0b_0000_0111_1101_0100,
						#	"B": 0b_0011_0001_1011_0100,
						#	"B": 0b_0000_1001_1001_1000,
						"B": 0b_0001_0111_1011_0100,
						"C": 0b_0001_0001_0001_0100,
						"D": 0b_1001_0100_0100_0110,
						"E": 0b_0001_0011_1001_0100,
						"F": 0b_0000_0011_1001_0100,
						"G": 0b_0001_0111_0001_0100,
						"H": 0b_0000_0111_1101_0000,
						"I": 0b_1001_0000_0000_0110,
						"J": 0b_0001_0101_0100_0000,
						"K": 0b_0010_0001_1011_0000,
						"L": 0b_0001_0001_0001_0000,
						"M": 0b_0000_0101_0111_1000,
						"N": 0b_0010_0101_0101_1000,
						"O": 0b_0001_0101_0101_0100,
						"P": 0b_0000_0011_1101_0100,
						"Q": 0b_0011_0101_0101_0100,
						"R": 0b_0010_0011_1101_0100,
						"S": 0b_0001_0110_1001_0100,
						"T": 0b_1000_0000_0000_0110,
						"U": 0b_0001_0101_0101_0000,
						"V": 0b_0000_1001_0011_0000,
						"W": 0b_0010_1101_0101_0000,
						"X": 0b_0010_1000_0010_1000,
						"Y": 0b_1000_0000_0010_1000,
						"Z": 0b_0001_1000_0010_0100,
						"0": 0b_0001_1101_0111_0100,
						"1": 0b_0000_0100_0100_0000,
						"2": 0b_0001_0011_1100_0100,
						"3": 0b_0001_0110_1100_0100,
						"4": 0b_0000_0110_1101_0000,
						"5": 0b_0001_0110_1001_0100,
						"6": 0b_0001_0111_1001_0100,
						"7": 0b_0000_0100_0100_0100,
						"8": 0b_0001_0111_1101_0100,
						"9": 0b_0001_0110_1101_0100,
						".": 0b_0100_0000_0000_0000,
						"'": 0b_0100_0000_0000_0001,
						"+": 0b_1000_0010_1000_0010,
						"-": 0b_0000_0010_1000_0000,
						"*": 0b_0010_1010_1010_1000,
						"|": 0b_1000_0000_0000_0010,
						"/": 0b_0000_1000_0010_0000,
						"\\": 0b_0010_0000_0000_1000,
						}
		


from	machine		import	Pin, I2C, Timer
#from	nxp_periph	import	PCA8561
from	utime		import	sleep	

def main():
	i2c		= I2C( 0, freq = (400 * 1000) )
	print( i2c.scan() )
	
	lcd	= PCA8561( i2c )
	
	lcd.write_registers( "Display_ctrl_1", 0x01 )
	lcd.write_registers( "COM0_07_00", [ 0xFF ] * 12 )
	lcd.write_registers( "COM0_07_00", [ 0x00 ] * 12 )
	lcd.write_registers( "COM0_07_00", [ 0x00, 0x00, 0xFF ] * 4 )
	sleep( 0 )

	for c in range( 4 ):
		for s in range( 18 ):
			lcd.com_seg( c, s, 1 )
			sleep( 0.1 )

	for c in range( 4 ):
		for s in range( 18 ):
			lcd.com_seg( c, s, 0 )
			sleep( 0.1 )

	test	= [ chr( i ) for i in range( ord( "0" ), ord( "9" ) + 1 ) ]
	test	= [ ".", "'", "+" ] + [ "-", "\\", "|", "/" ] * 5
	test	= [ chr( i ) for i in range( ord( "A" ), ord( "Z" ) + 1 ) ]

	while True:

		lcd.puts( "+-*/" )
		lcd.puts( "    test    ", char_per_sec = 4 )	#	will be converted to uppercase
		sleep( 1 )

		for i in range( 10000 ):
			lcd.puts( "{:4}".format( i ) )

		sleep( 0.5 )
		lcd.clear()

		for c in test:
			lcd.putchar( c )
			sleep( 0.2 )

		sleep( 0.5 )
		lcd.clear()
		
	
if __name__ == "__main__":
	main()
