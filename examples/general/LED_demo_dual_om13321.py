import	os
import	math
from	machine		import	I2C, Timer
from	nxp_periph	import	PCA9956B, LED

IREF_INIT	= 0x10

def main():
	print( "Demo is running on {}".format( os.uname().machine ) )

	i2c		= I2C( 0, freq = (400 * 1000) )
	dev_adr	= ( 0x02, 0x04 )
	
	led_c	= []
	leds	= []
	for adr in dev_adr:
		dev		 = PCA9956B( i2c, adr >> 1, iref = IREF_INIT )
		leds	+= [ LED( dev, i ) for i in range( dev.CHANNELS ) ]
		led_c 	+= [ dev ]
		print( dev.info() )
	
	print( "total {} LEDs are controlled".format( len( leds ) ) )
	om13321_order	= ( ( 0, 1, 2 ), ( 3, 4, 5 ), ( 6, 7, 8 ), ( 9, 10, 11 ), ( 12, 13, 14 ), ( 15, 16, 17 ), ( 18, 19, 20 ), ( 21, 22, 23 ) )
	
	color_led_idx	= tuple()
	for i in ( 0, 24, 36, 12 ):
		color_led_idx	+= tuple( tuple( c for c in range( n, n + 3 ) ) for n in range( i, i + 12, 3 ) )

	c_demo	= Color_demo( [ [leds[ i ] for i in u] for u in color_led_idx ], buffered = True )

	while True:
		pass


class Color_demo:
	def __init__( self, leds, sample_length = 60, miliseconds = 20, buffered = False ):
		self.RGB		= 3
		self.leds		= leds
		self.units		= len( leds )
		self.length		= sample_length
		self.pattern	= [ 0.5 - 0.5 * math.cos( 2 * math.pi * x / self.length ) for x in range( self.length ) ]
		self.pattern	= [ x * x for x in self.pattern ]
		self.count		= 0

		led_list		= sum( leds, [] )
		self.dev_list	= []
		
		for led in led_list:
			if led.__dev not in self.dev_list:
				self.dev_list	+= [ led.__dev ]
		
		if 0 != self.units:
			self.t	= Timer( -1 )
			self.t.init( period = miliseconds, mode = Timer.PERIODIC, callback = self.change_buffered if buffered else self.change_indivisual )
		
	def change_indivisual( self, x ):
		for i, u in zip( range( self.units ), self.leds ):
			p	= (self.count + i * (self.length // self.units)) % self.length
			for c, e in zip( range( self.RGB ), u ):
				e.v	= self.pattern[ (p + (c * self.length // self.RGB)) % self.length ]
			
		self.count	= (self.count + 1) % self.length

	def change_buffered( self, x ):
		for i, u in zip( range( self.units ), self.leds ):
			p	= (self.count + i * (self.length // self.units)) % self.length
			for c, e in zip( range( self.RGB ), u ):
				e.b	= self.pattern[ (p + (c * self.length // self.RGB)) % self.length ]

		for dev in self.dev_list:
			dev.flush()
			
		self.count	= (self.count + 1) % self.length

if __name__ == "__main__":
	main()




