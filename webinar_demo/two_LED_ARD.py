import	os
import	math
from	machine		import	Pin, I2C, SPI, SoftSPI, Timer
from	nxp_periph	import	PCA9955B, PCA9957, LED, PCAL6416
from	utime		import sleep

IREF_INIT	= 0xFF

def main():
	print( "Demo is running on {}".format( os.uname().machine ) )

	i2c		= I2C( 0, freq = (400 * 1000) )
	spi		= SPI( 0, 1000 * 1000, cs = 0 )
	led0	= PCA9955B( i2c, 0xBC >>1, iref = IREF_INIT )
	led1	= PCA9957( spi, setup_EVB = True, iref = IREF_INIT )

	gpio	= PCAL6416( i2c )

	leds	 = [ LED( led0, i ) for i in range( led0.CHANNELS ) ]
	leds	+= [ LED( led1, i ) for i in range( led1.CHANNELS ) ]

	color_led_idx	= ( ( 0, 1, 2 ), ( 3, 4, 5 ), ( 6, 7, 8 ), ( 16, 17, 18 ), ( 19, 20, 21 ), ( 22, 23, 24 ), ( 25, 26, 27 ) )
	white_led_idx	= ( 9, 10, 11, 12, 13, 14, 15, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39 )
		
	c_demo	= Color_demo( [ [leds[ i ] for i in u] for u in color_led_idx ] )
	w_demo	= White_demo( [ leds[ i ] for i in white_led_idx ] )

	gpio.config	= [ 0x00, 0x00 ]
	pattern		= [ 0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40 ]
	pattern		= [ ~x for x in pattern ]
	count	= 0

	while True:
		gpio.value	= pattern[ count % len( pattern ) ]
		count += 1
		sleep( 0.05 )


class White_demo:
	def __init__( self, leds, sample_length = 30, miliseconds = 20 ):
		self.leds		= leds
		self.length		= sample_length
		self.units		= len( leds )
		self.u_idx		= 0
		self.steps		= 0

		"""
		self.pattern	= [ i / (self.length // 2) for i in range( self.length // 2 ) ]
		self.pattern   += [ 1.0 - i for i in self.pattern ]
		self.pattern.reverse()
		"""
		self.pattern	= [ 2 ** -((8.0 * i) / self.length) for i in range( self.length ) ]
		
		if 0 != self.units:
			self.t	= Timer( 1 )
			self.t.init( period = miliseconds, mode = Timer.PERIODIC, callback = self.change )

	def change( self, x ):
		self.leds[ self.u_idx ].v	= self.pattern[ self.steps ]

		self.steps	= (self.steps + 1) % self.length
		if 0 == self.steps:
			self.u_idx	= (self.u_idx + 1) % self.units


class Color_demo:
	def __init__( self, leds, sample_length = 60, miliseconds = 20 ):
		self.RGB		= 3
		self.leds		= leds
		self.units		= len( leds )
		self.length		= sample_length
		self.pattern	= [ 0.5 - 0.5 * math.cos( 2 * math.pi * x / self.length ) for x in range( self.length ) ]
		self.pattern	= [ x * x for x in self.pattern ]
		self.count		= 0

		if 0 != self.units:
			self.t	= Timer( 0 )
			self.t.init( period = miliseconds, mode = Timer.PERIODIC, callback = self.change )
		
	def change( self, x ):
		for i, u in zip( range( self.units ), self.leds ):
			p	= (self.count + i * (self.length // self.units)) % self.length
			for c, e in zip( range( self.RGB ), u ):
				e.v	= self.pattern[ (p + (c * self.length // self.RGB)) % self.length ]

		self.count	= (self.count + 1) % self.length

if __name__ == "__main__":
	main()
