from	machine		import	Pin, I2C
from	nxp_periph	import	PCF2131

def main():
	i2c	= I2C( 0, freq = (400 * 1000) )
	rtc	= PCF2131( i2c )
	
	print( rtc.info() )
	print( "=== operation start ===" )
	print( "oscillator_stopped ? : {}".format( rtc.oscillator_stopped() ) )

	print( rtc.datetime() )
	rtc.dump_reg()
	
	rtc.battery_switchover( True )

	rtc.init( ( 2017, 9, 14 ) )
	print( rtc.datetime() )

	rtc.deinit()
	print( rtc.datetime() )

	rtc.datetime( (2022, 12, 21, 21, 23, 32, 99, None ), 1 )
	print( rtc.datetime() )
	print( rtc.now() )

	test_interrupt( rtc )


def test_interrupt( rtc ):
	int_flag	= False

	def callback( pin_obj ):
		nonlocal	int_flag
		int_flag	= True
		
	rtc.interrupt_clear()

	intA	= Pin( "D8", Pin.IN )
	intA.irq( trigger = Pin.IRQ_FALLING, handler = callback )
	
	intB	= Pin( "D9", Pin.IN )
	intB.irq( trigger = Pin.IRQ_FALLING, handler = callback )
	
	rtc.periodic_interrupt( "A" )

	t	= rtc.datetime()
	alarm_time	= {
						"hours"		: t[4],
						"minutes"	: t[5],
						"seconds"	: (t[6] + 5) % 60,
				  }
	rtc.alarm_int( "B", **alarm_time )

	rtc.set_timestamp_interrupt( "B", 1 )

	rtc.dump_reg()

	count	= 0

	while True:
		if int_flag:
			event	= rtc.interrupt_clear()
			int_flag	= False

			event	= rtc.check_events( event )
			
			for e in event:
				print( "{} {}".format( e, rtc.datetime() ) )

			if "ts1" in event:
				rtc.dump_reg()
				
				for i in range( 1, 5 ):
					print( "timestamp{} = {}".format( i, rtc.timestamp( i ) ) )

			count += 1
			
			if 0 == count % 10:
				rtc.dump_reg()

if __name__ == "__main__":
	main()
