from	machine		import	Pin, I2C, SoftI2C
from	nxp_periph	import	PCF85053A
import	machine

def main():
	intf	= SoftI2C( sda = "D14", scl = "D15", freq = (400_000) )
	rtc	= PCF85053A( intf )

	print( rtc.info() )
	print( "=== operation start ===" )
	
	osf	= rtc.oscillator_stopped()
	print( "rtc.oscillator_stopped()\n  --> ", end = "" )
	print( osf )

	machine_rtc	= machine.RTC()
	if osf:
		source, target, msg	= machine_rtc, rtc, "stop is detected"
		feature_test( rtc )
	else:
		source, target, msg	= rtc, machine_rtc,  "was kept running"

	target.datetime( source.datetime() )
	print( "since RTC device oscillator {}, Date&Time symchronized : {} --> {}".format( msg, source, target ) )

	print( "rtc.now()\n --> ", end = "" )
	print( rtc.now() )

	demo( rtc )

def feature_test( rtc ):
	print( "\nDate&Time register operation test:" )

	print( "rtc.datetime()\n --> ", end = "" )
	print( rtc.datetime() )
	
	rtc.init( ( 2017, 9, 14 ) )
	print( "tc.init( ( 2017, 9, 14 )\n --> ", end = "" )
	print( rtc.datetime() )

	rtc.deinit()
	print( "rtc.deinit()\n --> ", end = "" )
	print( rtc.datetime() )

	rtc.datetime( (2022, 12, 21, 21, 23, 32, 99, None ), 1 )
	print( "rtc.datetime( (2022, 12, 21, 21, 23, 32, 99, None ), 1 )\n --> ", end = "" )
	print( rtc.datetime() )

	print( "rtc.now()\n --> ", end = "" )
	print( rtc.now() )

	print( "" )

def demo( rtc ):
	int_flag	= False

	def callback( pin_obj ):
		nonlocal	int_flag
		int_flag	= True
		
	rtc.interrupt_clear()

	intr	= Pin( "D2", Pin.IN )
	intr.irq( trigger = Pin.IRQ_FALLING, handler = callback )

	rtc.periodic_interrupt( period = 1 )

#	alm	= rtc.timer_alarm( seconds = 5 )
#	print( "alarm is set = {}".format( ", ".join( alm ) ) )

	while True:
		if int_flag:
			event	= rtc.interrupt_clear()
			int_flag	= False

			event	= rtc.check_events( event )
			
			dt	= rtc.datetime()
			
			for e in event:
				print( "{} {}".format( e, dt ), end = "\r" if e is "periodic" else "\n" )

			if "alarm" in event:
				print( "!!!!!!! ALARM !!!!!!!" )
				alm	= rtc.timer_alarm( seconds = 5 )
				print( "new alarm seting = {}".format( ", ".join( alm ) ) )

			if not dt[ 6 ] % 30:
				rtc.dump_reg()

if __name__ == "__main__":
	main()

