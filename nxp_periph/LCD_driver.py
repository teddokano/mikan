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
		Parameters
		----------
		i2c		: I2C instance
		address	: int, option

		"""
		super().__init__( i2c, address )
	
	def com_seg( self, com, seg ):
		reg	= [	[ "COM0_07_00", "COM0_15_08", "COM0_17_16" ],
				[ "COM1_07_00", "COM1_15_08", "COM1_17_16" ],
				[ "COM2_07_00", "COM2_15_08", "COM2_17_16" ],
				[ "COM3_07_00", "COM3_15_08", "COM3_17_16" ]
				]

		com	= 3

		if seg is 3:
			for i in range( 10 ):
				self.write_registers( reg[ com ][ seg // 8 ], 0x00 )
				sleep( 0.1 )
				self.write_registers( reg[ com ][ seg // 8 ], 0x01 << (seg % 8) )
				sleep( 0.1 )


		self.write_registers( reg[ com ][ seg // 8 ], 0x00 )
		sleep( 0.1 )
		self.write_registers( reg[ com ][ seg // 8 ], 0x01 << (seg % 8) )
	
	
	def char_pattern( self, c ):
		charset	= {	"A": 0b_0000_0111_1101_0100,
#					"B": 0b_0011_0001_1011_0100,
					"B": 0b_0000_1001_1001_1000,
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
					" ": 0b_0000_0000_0000_0000,
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
					"-": 0b_0000_0010_1000_0000,
					"+": 0b_1000_0010_1000_0010,
					"|": 0b_1000_0000_0000_0010,
					"/": 0b_0000_1000_0010_0000,
					"\\": 0b_0010_0000_0000_1000,
					}

		self.write_registers( "COM0_07_00",  charset[ c ]        & 0x0F )
		self.write_registers( "COM1_07_00", (charset[ c ] >>  4) & 0x0F )
		self.write_registers( "COM2_07_00", (charset[ c ] >>  8) & 0x0F )
		self.write_registers( "COM3_07_00", (charset[ c ] >> 12) & 0x0F )


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

	"""
	while True:
		for c in range( 4 ):
			for s in range( 18 ):
				lcd.com_seg( c, s )
	"""
	
	test	= [ chr( i ) for i in range( ord( "0" ), ord( "9" ) + 1 ) ]
	test	= [ ".", "'", "+" ] + [ "-", "\\", "|", "/" ] * 5
	test	= [ chr( i ) for i in range( ord( "A" ), ord( "Z" ) + 1 ) ]

	while True:
		for c in test:
			lcd.char_pattern( c )
			sleep( 0.2 )
		
	
if __name__ == "__main__":
	main()
