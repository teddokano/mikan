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
	gpio	= PCAL6408( i2c, setup_EVB = True )

	print( i2c.scan() )

	gpio.dump_reg()

	gpio.config( 0xF0 )	
	gpio.write_registers( "Interrupt mask", 0x0F )

	tim0 = Timer(0)
	tim0.init( period= 10, callback = tim_cb)

	count	= 0

	while True:
		if int_flag:
			print( "\n--- inetrupt:" )
			print( "  Interrupt status = {:08b}".format( gpio.read_registers( "Interrupt status", 1 ) ) )
			print( "  Input Port       = {:08b}".format( gpio.read_registers( "Input Port", 1 ) ) )
			int_flag	= False

		if tim_flag:
			tim_flag	= False

			gpio.value	= count
			count		+= 1
			if count is 16:
				count	= 0
			
			print( "port read = {:08b}".format( gpio.value ), end = "\r" )



def demo16():
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
	gpio	= PCAL6408( i2c, setup_EVB = True )

	print( i2c.scan() )

	gpio.dump_reg()

	#	port0 is output, port1 is input
	#	check operation by connecting port0 pin to port1 pin
	
#	gpio.config( [ 0x00, 0xFF ] )
#	gpio.write_registers( "Interrupt mask register 1", 0x00 )

	gpio.config( 0xF0 )	
	gpio.write_registers( "Interrupt mask", 0x0F )


	tim0 = Timer(0)
	tim0.init( period= 10, callback = tim_cb)

	count	= 0


	while True:
		if int_flag:
#			print( "\n--- inetrupt: status = {:08b}".format( gpio.read_registers( "Interrupt status register 1", 1 ) ) )
#			print( "\n--- inetrupt: status = {:08b}".format( gpio.read_registers( "Interrupt status", 1 ) ) )
			print( "\n--- inetrupt:" )
			print( "  Interrupt status = {:08b}".format( gpio.read_registers( "Interrupt status", 1 ) ) )
			print( "  Input Port       = {:08b}".format( gpio.read_registers( "Input Port", 1 ) ) )
			int_flag	= False

		if tim_flag:
			tim_flag	= False
#			gpio.value	= [ i, i ]
#			utime.sleep( 0.01 )


			gpio.value	= count
			count		+= 1
			if count is 256:
				count	= 0
			
			r	= gpio.value
			
			if type( r ) == int:
				print( "port read = {:08b}".format( r ), end = "\r" )
			else:
				print( "port read = {}".format( [ "{:08b}".format( i ) for i in r ] ), end = "\r" )

if __name__ == "__main__":
	main()
