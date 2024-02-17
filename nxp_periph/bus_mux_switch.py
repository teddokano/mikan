from nxp_periph.interface	import	I2C_target

class BusMuxSwitch_base():
	pass

class PCA9846( BusMuxSwitch_base, I2C_target ):
	DEFAULT_ADDR	= 0xE2 >> 1
	N_CH			= 4

	CH0	= 0x01
	CH1	= 0x02
	CH2	= 0x04
	CH3	= 0x08
	
	def __init__( self, i2c, address = DEFAULT_ADDR ):
		"""
		Initializer for PCA9846 class instance

		Parameters
		----------
		i2c		: I2C instance
		address	: int, option

		"""
		super().__init__( i2c, address )
		
	def select( self, sel = None ):
		"""
		channel select
	
		Parameters
		----------
		sel : int or None
			Bit pattern to select channels.
			0b0001 is to enable channel 0, 0b0010 for ch2..
			If this parameter is not given, it will return current setting bit pattern
				
		Returns
		-------
		int : Bit pattern if no parameter given


		"""
		if sel is None:
			return self.receive( 1 )[ 0 ]
		else:
			self.send( [ sel ] )

def main():
	from machine import I2C
	from utime import sleep
	from nxp_periph import M24C02

	i2c		 = I2C( 0, freq = 400_000 )
	sw		= PCA9846( i2c )
	
	eeproms = [
				M24C02( i2c, 0xA0 >> 1 ),
				M24C02( i2c, 0xA2 >> 1 ),
				M24C02( i2c, 0xA4 >> 1 ),
				M24C02( i2c, 0xA6 >> 1 )
	]

	sw.select( PCA9846.CH3 | PCA9846.CH2 | PCA9846.CH1 | PCA9846.CH0 )

	### Select all channels and write each EEPROM
	
	for i, e in enumerate( eeproms ):
		print( f"[eeprom in ch{i}] {e.info()}" )
		length	= e.write( 0, f"[eeprom in ch{i}] Hello, BusSwitch PCA9846! This is a demo code for the BusSwitch_PCA9846PW-ARD board." )

	while True:
	
		### Select all channels and read all EEPROMs
	
		sw.select( PCA9846.CH3 | PCA9846.CH2 | PCA9846.CH1 | PCA9846.CH0 )
		print( f"\nall channels enabled (sw.select() → 0b{sw.select():04b}):" )
		
		for i, e in enumerate( eeproms ):
			if e.ping():	# Need to ping to re-enable the device which has been NACKed
				read_data = e.read( 0, length )
				print( "".join( map( chr, read_data ) ) )

		sleep( 1 )
		
		### Select one channel and try to read all EEPROMs

		for i in range( sw.N_CH ):
		
			sw.select( 0x01 << i )
			print( f"\nchannel {i} is enabled (sw.select() → 0b{sw.select():04b}):" )
		
			for e in eeproms:
				if e.ping():
					read_data = e.read( 0, length )
					print( "".join( map( chr, read_data ) ) )

			sleep( 1 )
	
if __name__ == "__main__":
	main()
