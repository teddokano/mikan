from	machine		import	SPI, Pin
from	utime		import	sleep
from	struct		import	unpack
from nxp_periph.interface	import	SPI_target

WAIT	= 0.001
#WAIT	= 0
CWAIT	= 0

class AFE_base:
	pass

class NAFE13388( AFE_base, SPI_target ):
	ch_cnfg_reg	= [ 0x0020, 0x0021, 0x0022, 0x0023 ]

	def __init__( self, spi, cs = None ):
		SPI_target.__init__( self, spi, cs )
#		self.spi	= spi

		self.reset_pin	= Pin( "D6", Pin.OUT )
		self.syn_pin	= Pin( "D5", Pin.OUT )
		self.drdy_pin	= Pin( "D3", Pin.IN )
		self.int_pin	= Pin( "D2", Pin.IN )

		self.reset_pin.value( 1 )
		self.syn_pin.value( 1 )
		
		self.reset()
		self.boot()
		
		self.logical_channel	= [
									self.logical_ch_config( 0, [ 0x11F0, 0x0040, 0x1400, 0x0000 ] ),
									self.logical_ch_config( 1, [ 0x33F0, 0x0040, 0x4100, 0x3060 ] ),
									]
		
		self.weight_offset	= -172.7
		self.weight_coeff	= 1044 / (10388.61 - self.weight_offset)

		self.temperature_offset	= -1600
		self.temperature_coeff	= 1 / 1000
		self.temperature_base	= 25

	def start_ADC( self ):
		self.write_r16( 0x2003 )


	def	write_r16( self, reg, val = None ):
		reg		<<= 1
	
		regH	= reg >> 8 & 0xFF
		regL	= reg & 0xFF

		if val:
			valH	= val >> 8 & 0xFF
			valL	= val & 0xFF
			self.send( [ regH, regL, valH, valL ] )
		else:
			self.send( [ regH, regL ] )

	def	read_r16( self, reg ):
		reg		<<= 1
		reg		|= 0x4000
		regH	= reg >> 8 & 0xFF
		regL	= reg & 0xFF

		data	= bytearray( [ regH, regL, 0xFF, 0xFF ] )
		self.__if.write_readinto( data, data )
		
		return unpack( ">H", data[2:] )[ 0 ]

	def	read_r24( self, reg ):
		reg		<<= 1
		reg		|= 0x4000
		regH	= reg >> 8 & 0xFF
		regL	= reg & 0xFF

		data	= bytearray( [ regH, regL, 0xFF, 0xFF, 0xFF ] )
		self.__if.write_readinto( data, data )

		data	+= b'\x00'		
		data	= unpack( ">l", data[2:] )[ 0 ] >> 8

		return data

	def boot( self ):
		reg_init	= [
						{	0x0010: None, 
							0x002A: 0x0000,
							0x002B: 0x0000,
							0x002C: 0x0000,
							0x002F: 0x0000,
							0x0029: 0x0000,
							},
					   {	0x0030: 0x0010, 
							},
					]
					
		for step in reg_init:
			for k, v in step.items():
				self.write_r16( k, v )
			sleep( 0.001 )

	def reset( self ):
		self.write_r16( 0x0014 )
		sleep( 0.001 )

	def dump( self, list ):
		for r in list:
			if r:
				print( "0x{:04X} = {:04X}".format( r, self.read_r16( r ) ) )
			else:
				print( "" )

	def stable_read( self, ch, over_sample = 10 ):
		r			= 0
		for _ in range( over_sample ):
			r	+= self.read( ch )
		
		return r / over_sample

	def temperature( self ):
		t	= self.stable_read( 0 )
		return (t - self.temperature_offset) * self.temperature_coeff + self.temperature_base
		
	def weight( self ):
		w	= self.stable_read( 1 )
		return (w - self.weight_offset) * self.weight_coeff

	def logical_ch_config( self, logical_channel, list ):
		self.write_r16( 0x0000 + logical_channel )

		for r, v in zip( self.ch_cnfg_reg, list ):
			self.write_r16( r, v )
		self.dump( [ 0x20, 0x21, 0x22, 0x23 ] )
		
		mask	= 1
		bits	= self.read_r16( 0x24 ) | mask << logical_channel
		self.write_r16( 0x24, bits )
		
		print( f"bits = {bits}" )
		
		self.num_logcal_ch	= 0
		for i in range( 16 ):
			if bits & (mask << i):
				self.num_logcal_ch	+= 1
		
		print( f"self.num_logcal_ch = {self.num_logcal_ch}" )
		

	def read( self ):
		reg		= 0x2003 << 1
		regH	= reg >> 8 & 0xFF
		regL	= reg & 0xFF

		data	= bytearray( [ regH, regL ] + ([ 0xFF ] * (3 * self.num_logcal_ch) ) )

		self.__if.write_readinto( data, data )

		values	= []
		
		for i in range( self.num_logcal_ch ):
			offset	= 2 + 3 * i
			v		= data[ offset : offset + 3 ]
			v		+= b'\x00'		
			values	+= [ unpack( ">l", v )[ 0 ] >> 8 ]
		"""
		
#		self.logical_ch_config( 0, [ 0x11F0, 0x0040, 0x1400, 0x0000 ] )
		self.write_r16( 0x2000 )
		sleep( 0.001 )
		values	+= [ self.read_r24( 0x2040 ) ]
#		self.logical_ch_config( 1, [ 0x33F0, 0x0040, 0x4100, 0x3060 ] )
		self.write_r16( 0x2000 )
		sleep( 0.001 )
		values	+= [ self.read_r24( 0x2041 ) ]
		"""

		values	+= [ self.read_r24( 0x2040 ) ]
		values	+= [ self.read_r24( 0x2041 ) ]
		
		print( values )

		return values

def main():
	spi	= SPI( 0, 1000_000, cs = 0, phase = 1 )

	afe	= NAFE13388( spi, None )
	afe.dump( [ 0x7C, 0x7D, 0x7E, 0xAE, 0xAF, 0x34, 0x37, None, 0x30, 0x31 ] )
	
	afe.start_ADC()
	
	count	= 0
	
	while True:
		afe.read()
#		t, w	= afe.read()
#		print( "{:.2f}  {:.2f}".format( t, w ) )
		count	+= 1
		sleep( 0.1 )

if __name__ == "__main__":
	main()
