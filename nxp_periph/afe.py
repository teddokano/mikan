from	machine		import	SPI, Pin, Timer
from	utime		import	sleep, sleep_ms, sleep_us
from	struct		import	unpack
from	micropython	import	schedule
from nxp_periph.interface	import	SPI_target

WAIT	= 0.001
#WAIT	= 0
CWAIT	= 0

class AFE_base:
	pass

class NAFE13388( AFE_base, SPI_target ):
	ch_cnfg_reg	= [ 0x0020, 0x0021, 0x0022, 0x0023 ]

	def __init__( self, spi, cs = None ):
		self.tim_flag	= False
		self.cb_count	= 0

		SPI_target.__init__( self, spi, cs )

		self.reset_pin	= Pin( "D6", Pin.OUT )
		self.syn_pin	= Pin( "D5", Pin.OUT )
		self.drdy_pin	= Pin( "D3", Pin.IN )
		self.int_pin	= Pin( "D2", Pin.IN )

		self.reset_pin.value( 1 )
		self.syn_pin.value( 1 )
		
		self.reset()
		self.boot()
		
		self.logical_channel	= [
									self.logical_ch_config( 0, [ 0x1150, 0x00AC, 0x1400, 0x0000 ] ),
									self.logical_ch_config( 1, [ 0x3350, 0x00A4, 0x1400, 0x3060 ] ),
									]

		self.setting	= { "weight": {}, "temperature": {}, "remark": "AFE demo updated setting file" }

		self.setting[ "weight"      ][ "ofst"  ]	= -38
		self.setting[ "weight"      ][ "coeff" ]	= 1044 / (354 - self.setting[ "weight" ][ "ofst" ])
		self.setting[ "temperature" ][ "ofst"  ]	= -70
		self.setting[ "temperature" ][ "coeff" ]	= 1 / 40
		self.setting[ "temperature" ][ "base"  ]	= 25

		self.coeff_microvolt	= ((10 / (2 ** 24)) / 0.8) * 1e6

		self.ch		= [ 0 ] * self.num_logcal_ch
		self.done	= False
		
		print( self.setting )
		
	def periodic_measurement_start( self ):
		tim0 = Timer(0)
		tim0.init( period= 100, callback = self.tim_cb )

	def sch_cb( self, _ ):
		ch_start	= (self.cb_count + 1) % 2
		ch_read		= self.cb_count % 2

		# read data
		self.ch[ ch_read ]	= self.read_r24( 0x2040 + ch_read )	* self.coeff_microvolt

		# start ADC operation
		self.write_r16( 0x0000 + ch_start )
		self.write_r16( 0x2000 )
		
		self.cb_count	+= 1
		
		if self.cb_count % 2:
			self.done	= True
	
	def tim_cb( self, tim_obj ):
		schedule( self.sch_cb, 0 )

	def	write_r16( self, reg, val = None ):
		reg		<<= 1
	
		regH	= reg >> 8 & 0xFF
		regL	= reg & 0xFF

		if val is None:
			self.send( [ regH, regL ] )
		else:
			valH	= val >> 8 & 0xFF
			valL	= val & 0xFF
			self.send( [ regH, regL, valH, valL ] )

	def	read_r16( self, reg, signed = False ):
		reg		<<= 1
		reg		|= 0x4000
		regH	= reg >> 8 & 0xFF
		regL	= reg & 0xFF

		data	= bytearray( [ regH, regL, 0xFF, 0xFF ] )
		self.__if.write_readinto( data, data )
		
		return unpack( ">h" if signed else ">H", data[2:] )[ 0 ]

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
			sleep( WAIT )

	def reset( self ):
		self.write_r16( 0x0014 )
		sleep( WAIT )

	def dump( self, list ):
		for r in list:
			if r:
				print( "0x{:04X} = {:04X}".format( r, self.read_r16( r ) ) )
			else:
				print( "" )

	def temperature( self ):
		t	= self.ch[ 0 ]
		
		if self.setting[ "temperature" ][ "select" ] == 0:
			base	= self.setting[ "temperature" ][ "base" ]
		elif self.setting[ "temperature" ][ "select" ] == 1:
			if self.setting[ "temperature" ][ "measured" ] is None:
				base	= self.setting[ "temperature" ][ "base" ]
			else:
				base	= self.setting[ "temperature" ][ "measured" ]
		else:
			base	= self.die_temp()
			
		return (t - self.setting[ "temperature" ][ "ofst" ]) * self.setting[ "temperature" ][ "coeff" ] + base
		
	def weight( self ):
		w	= self.ch[ 1 ]
		return (w - self.setting[ "weight" ][ "ofst" ]) * self.setting[ "weight" ][ "coeff" ]

	def weight_zero( self ):
		w	= self.ch[ 1 ]
		self.setting[ "weight" ][ "ofst" ]	= w

	def weight_cal( self, ref ):
		w	= self.ch[ 1 ]
		self.setting[ "weight" ][ "coeff" ]	= ref / (w - self.setting[ "weight" ][ "ofst" ])

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
		
	def measure( self, ch = None ):
		if ch is not None:
			self.write_r16( 0x0000 + ch )
			self.write_r16( 0x2000 )
			sleep_ms( 100 )
			return self.read_r24( 0x2040 + ch ) * self.coeff_microvolt
		
		values	= []

		command	= 0x2004

		for i in range( self.num_logcal_ch ):
			self.write_r16( command )
			"""
			print( f"after command" )
			for i in range( 100 ):
				print( f"0x31 = {self.read_r16( 0x31 ):04X}" )
				sleep_us( 10 )
			"""
			sleep_ms( 10 )
			values	+= [ self.read_r24( 0x2040 + i ) ]
		
		print( values )

		return values
		
	def read( self, ch = None ):
		values	= []

		for i in range( self.num_logcal_ch ):
			values	+= [ self.read_r24( 0x2040 + i ) ]
		
		print( values )

		return values
	
	def die_temp( self ):
		return self.read_r16( 0x34, signed = True ) / 64
		
def main():
	spi	= SPI( 0, 1000_000, cs = 0, phase = 1 )

	afe	= NAFE13388( spi, None )
	afe.dump( [ 0x7C, 0x7D, 0x7E, 0xAE, 0xAF, 0x34, 0x37, None, 0x30, 0x31 ] )
	
	count	= 0

	afe.periodic_measurement_start()

	while True:
#		afe.measure( 0 )
		
		
#		t, w	= afe.read()
#		print( "{:.2f}  {:.2f}".format( t, w ) )
#		print( f"{count},  {afe.measure( 1 )},  {afe.measure( 2 )},  {afe.measure( 3 )}" )
#		print( f"{count},  {afe.measure( 0 )},  {afe.measure( 1 )},  {afe.measure( 2 )}" )
#		print( f"{count},  {afe.measure( 0 )},  {afe.measure( 1 )}" )
#		print( f"{count},  {afe.measure( 0 )},  {afe.measure( 1 )}" )

		if afe.done:
			afe.done	= False
#			print( f"{count},  {afe.ch[ 0 ]},  {afe.ch[ 1 ]}" )
			print( f"{afe.temperature()},  {afe.weight()}" )
			
		count	+= 1

if __name__ == "__main__":
	main()
