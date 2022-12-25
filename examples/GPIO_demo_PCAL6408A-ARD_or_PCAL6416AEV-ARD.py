from	machine		import	Pin, I2C, Timer
from	nxp_periph	import	PCAL6416, PCAL6408
import	utime

def main():
	int_flag	= False
	tim_flag	= False

	def callback( pin_obj ):
		nonlocal	int_flag
		int_flag	= True
		
	def tim_cb( tim_obj ):
		nonlocal	tim_flag
		tim_flag	= True
		
	int_pin	= Pin( "D10", Pin.IN )
	int_pin.irq( trigger = Pin.IRQ_FALLING, handler = callback )

	i2c		= I2C( 0, freq = (400 * 1000) )
#	gpio	= PCAL6408( i2c, setup_EVB = True )
	gpio	= PCAL6416( i2c, setup_EVB = True )

	if gpio.N_PORTS is 1:
		io_config_and_pull_up	= 0xF0
		int_mask_config			= 0x0F
	else:
		io_config_and_pull_up	= [ 0x00, 0xFF ]
		int_mask_config			= [ 0xFF, 0x00 ]


	gpio.config		= io_config_and_pull_up
	gpio.pull_up	= io_config_and_pull_up
	gpio.mask		= int_mask_config
	gpio.pull_en	= [ 0xFF ] * gpio.__np


	tim0 = Timer(0)
	tim0.init( period= 10, callback = tim_cb)

	count	= 0

	while True:
		if int_flag:
			int_flag	= False
			status		= gpio.status
			value		= gpio.value
			print( "\n--- inetrupt:" )
			
			if type( status ) == int:
				print( "  Interrupt status = 0b{:08b}".format( status ) )
				print( "  Input Port       = 0b{:08b}".format( value  ) )
			else:
				print( "  Interrupt status = {}".format(  [ "0b{:08b}".format( i ) for i in status ]  ) )
				print( "  Input Port       = {}".format(  [ "0b{:08b}".format( i ) for i in value ]   ) )
				
		if tim_flag:
			tim_flag	= False

			gpio.value	= count
			count		= (count + 1) & 0xFF
			
			r	= gpio.value

			if type( r ) == int:
				print( "port read = 0b{:08b}".format( gpio.value ), end = "\r" )
			else:
				print( "port read = {}".format( [ "0b{:08b}".format( i ) for i in r ] ), end = "\r" )
				

if __name__ == "__main__":
	main()
