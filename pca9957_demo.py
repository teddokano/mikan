"""
Serial interface management library for MicroPython
Akifumi (Tedd) OKANO / Released under the MIT license

version	0.1 (01-Oct-2022)
"""
import	os
import	math
from	machine		import	Pin, SPI, SoftSPI, Timer
from	nxp_periph	import	PCA9957, LED


def main():
	print( "Demo is running on {}".format( os.uname().machine ) )

#	spi		= SPI( 1, SPI_target.FREQ, sck = Pin( 10 ), mosi = Pin( 11 ), miso = Pin( 12 ) )
	spi		= SoftSPI( baudrate = 1000*1000, mosi = Pin( "D6" ), miso = Pin( "D3" ), sck = Pin( "D7" ) )
	cs		= Pin( "D4" )

	led_c	= PCA9957( spi, cs, iref = 0x10 )

	print( led_c.info() )
	led_c.dump_reg()
	
	leds	= [ LED( led_c, i ) for i in range( led_c.CHANNELS ) ]

	c_demo	= Color_demo( leds )
	w_demo	= White_demo( leds )


	tim0	= Timer( 0 )
	tim1	= Timer( 1 )
	tim0.init( period = 20, mode = Timer.PERIODIC, callback = c_demo.change )
	tim1.init( period = 50, mode = Timer.PERIODIC, callback = w_demo.change )

	while True:
		pass


class White_demo:
	def __init__( self, leds ):
		self.leds		= leds
		self.count		= 0
		self.offset		= 12

	def change( self, x ):
		idx	= (self.count >> 1) + self.offset
		self.leds[ idx ].v		= float( ~self.count & 0x1 )

		self.count	= (self.count + 1) % 24


class Color_demo:
	def __init__( self, leds ):
		self.leds			= leds
		self.SAMPLE_LENGTH	= 60
		self.UNITS			= 4
		self.RGB			= 3
		self.pattern	= [ 0.5 - 0.5 * math.cos( 2 * math.pi * x / self.SAMPLE_LENGTH ) for x in range( self.SAMPLE_LENGTH ) ]
		self.pattern	= [ x * x for x in self.pattern ]
		self.count		= 0
		
	def change( self, x ):
		for j in range( self.UNITS ):
			p	= (self.count + j * (self.SAMPLE_LENGTH // self.UNITS)) % self.SAMPLE_LENGTH
			for c in range( self.RGB ):
				self.leds[ c + j * self.RGB ].v	= self.pattern[ (p + (c * self.SAMPLE_LENGTH // self.RGB)) % self.SAMPLE_LENGTH ]

		self.count	= (self.count + 1) % self.SAMPLE_LENGTH


if __name__ == "__main__":

	main()
