from machine	import	Pin, I2C
import	utime


class I2C_Character_LCD:
	def __init__( self, i2c, address ):
		self.i2c			= i2c
		self.address		= address
		self.blank			= "".join( [ " " for _ in range( self.width ) ] )
		self.device_present	= True
		
		self.backlightpin	= Pin( "A3", Pin.OUT )
		self.backlight()
		
	def send( self, data_flag, value ):
		if self.device_present:
			try:
				self.i2c.writeto( self.address, bytearray( [ self.data_byte if data_flag else self.command_byte, value ] ) )
			except Exception as e:
				self.device_present	= False
				print( "No LCD panel detected" )

	def command( self, command ):
		self.send( False, command )
		utime.sleep_us( 27 )
		utime.sleep_ms( 1 )

	def data( self, data ):
		self.send( True, data )
		utime.sleep_ms( 1 )

	def clear( self ):
		self.command( 0x01 )

	def putc( self, char ):
		self.data( char )

	def puts( self, str, line_num = 0 ):
		self.command( 0x80 + 0x40 * line_num )
		for c in str:
			self.putc( ord( c ) )

	def print( self, string ):
		if isinstance( string, str ):
			splt	= []
			for i in range( 0, self.width * self.lines, self.width ):
				splt	+= [ string[ i : i + self.width ] ]
			
			self.print( splt )
			
		else:
			for i, s in enumerate( string ):
				if s is not None:
					self.puts( s + self.blank, i )

	def backlight( self, on = True ):
		self.backlightpin.value( on )

class AE_AQM0802( I2C_Character_LCD ):
	DEFAULT_ADDR		= (0x7C >> 1)
	
	def __init__( self, i2c ):
		self.command_byte	= 0x00
		self.data_byte		= 0x40
		self.width			= 8
		self.lines			= 2
		super().__init__( i2c, self.DEFAULT_ADDR )
		
		init_commands		= [ [ 0x38, 0x39, 0x14, 0x7A, 0x54, 0x6C ], [0x38, 0x0C, 0x01 ] ]

		for seq in init_commands:
			for v in seq:
				self.command( v )
			
			utime.sleep_ms( 200 )
		
def main():
	i2c		= I2C( 0, freq = (400 * 1000) )
	lcd		= AE_AQM0802( i2c )
	
	print( os.uname().machine + " is working!" )
	print( "available I2C target(s): ", end = "" )
	print( [ hex( i ) for i in i2c.scan() ] )

	while True:
		lcd.print( "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz" )
		utime.sleep( 1 )
		
		lcd.print( "192.168.100.222" )
		utime.sleep( 1 )
		
		lcd.print( "10.0.1.2" )
		utime.sleep( 1 )

		lcd.print( [ "ABCDEFGH", "12345678" ] )
		utime.sleep( 1 )
		
		lcd.print( [ "abcdefgh", None ] )
		utime.sleep( 1 )
		
		lcd.clear()
		utime.sleep( 1 )

		lcd.print( [ "ABCD", "1234" ] )
		utime.sleep( 1 )
		
		lcd.print( [ "abc", "" ] )
		utime.sleep( 1 )

		lcd.print( [ "", "ABC" ] )
		utime.sleep( 1 )
		
		for i in range( 10000 ):
			lcd.print( f"n={i}" )
		
if __name__ == "__main__":
	main()
