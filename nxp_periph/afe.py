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
	def __init__( self, spi, cs = None ):
		SPI_target.__init__( self, spi, cs )
		self.spi	= spi

		self.count	= 0
		
		self.reset_pin	= Pin( "D6", Pin.OUT )
		self.syn_pin	= Pin( "D5", Pin.OUT )
		self.drdy_pin	= Pin( "D3", Pin.IN )
		self.int_pin	= Pin( "D2", Pin.IN )

		self.reset_pin.value( 1 )
		self.syn_pin.value( 1 )
		
		self.logical_channel	= [
#									AFE_LogicalChannel( self, 0, [ 0x1110, 0x0040, 0x1400, 0x0000, 0x0001 ] ),
#									AFE_LogicalChannel( self, 1, [ 0x3350, 0x0040, 0x4100, 0x3060, 0x0002 ] ),
									AFE_LogicalChannel( self, 0, [ 0x11F0, 0x0040, 0x1400, 0x0000, 0x0001 ] ),
									AFE_LogicalChannel( self, 1, [ 0x33F0, 0x0040, 0x4100, 0x3060, 0x0002 ] ),
									]
		
		self.weight_offset	= -172.7
		self.weight_coeff	= 1044 / (10388.61 - self.weight_offset)

		self.temperature_offset	= -1600
		self.temperature_coeff	= 1 / 1000
		self.temperature_base	= 25

		
	def	write_reg( self, reg, val = None ):
		reg		<<= 1
	
		regH	= reg >> 8 & 0xFF
		regL	= reg & 0xFF

		if val:
			valH	= val >> 8 & 0xFF
			valL	= val & 0xFF
			self.spi.write( bytearray( [ regH, regL, valH, valL ] ) )
		else:
			self.spi.write( bytearray( [ regH, regL ] ) )

	def	read_reg( self, reg ):
		reg		<<= 1
		reg		|= 0x4000
		regH	= reg >> 8 & 0xFF
		regL	= reg & 0xFF

		data	= bytearray( [ regH, regL, 0xFF, 0xFF ] )
		self.spi.write_readinto( data, data )

		return unpack( ">H", data[2:] )[ 0 ]

	def	read_data( self, reg ):
		reg		<<= 1
		reg		|= 0x4000
		regH	= reg >> 8 & 0xFF
		regL	= reg & 0xFF

		data	= bytearray( [ regH, regL, 0xFF, 0xFF, 0xFF ] )
		self.spi.write_readinto( data, data )

		data	+= b'\x00'		
		data	= unpack( ">l", data[2:] )[ 0 ] >> 8

		return data

	def boot( self ):
		self.write_reg( 0x0010 )
		self.write_reg( 0x002A, 0x0000 )
		self.write_reg( 0x002B, 0x0000 )
		self.write_reg( 0x002C, 0x0000 )
		self.write_reg( 0x002F, 0x0000 )
		self.write_reg( 0x0029, 0x0000 )
		sleep( 0.001 )
		self.write_reg( 0x0030, 0x0010 )
		sleep( 0.001 )

	def reset( self ):
		self.write_reg( 0x0014 )
		sleep( 0.001 )

	def dump( self, list ):
		for r in list:
			if r:
				print( "0x{:04X} = {:04X}".format( r, self.read_reg( r ) ) )
			else:
				print( "" )

	def read( self, ch ):
		return self.logical_channel[ ch ].read()

	def stable_read( self, ch, over_sample = 100 ):
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

class AFE_LogicalChannel:
	rlist	= [ 0x0020, 0x0021, 0x0022, 0x0023 ]
	
	def __init__( self, afe, ch, list ):
		self.afe	= afe
		self.ch		= ch
		self.cnfg	= list
		
	def read( self ):
		self.afe.write_reg( 0x0000 + self.ch )
		
		for r, v in zip( self.rlist, self.cnfg ):
			self.afe.write_reg( r, v )
		
		self.afe.write_reg( 0x2000 )
		sleep( 0.001 )
		return self.afe.read_data( 0x2040 + self.ch )

def main():
	spi	= SPI( 0, 1000_000, cs = 0, phase = 1 )

	afe	= NAFE13388( spi, None )
	afe.reset()
	afe.boot()
	
	afe.dump( [ 0x7C, 0x7D, 0x7E, 0xAE, 0xAF, 0x34, 0x37, None, 0x30, 0x31 ] )

	print( "ch 0" )
	afe.write_reg( 0x0000 )
	afe.dump( [ 0x20, 0x21, 0x22, 0x23 ] )

	print( "ch 1" )
	afe.write_reg( 0x0001 )
	afe.dump( [ 0x20, 0x21, 0x22, 0x23, 0x24 ] )
	
	count	= 0
	
	while True:
#		print( "{:.2f}, {:.2f}".format( afe.stable_read( 0 ), afe.stable_read( 1 ) ) )
#		print( "{:.2f}".format( afe.stable_read( 1 )-afe.weight_offset ) , end="    ")
#		print( "{:.2f}".format( afe.weight() ) )
		print( "{:.2f}  {:.2f}".format( afe.temperature(), afe.weight() ) )
		count	+= 1

if __name__ == "__main__":
	main()
