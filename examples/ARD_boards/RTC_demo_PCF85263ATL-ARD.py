from	machine		import	Pin, I2C, SPI
from	nxp_periph	import	PCF86263A, RTC_base
import	machine
import time

BAT_SWOVR	= True

def main():
	intf	= I2C( 0, freq = (400 * 1000) )
	rtc		= PCF86263A( intf )

	rtc.dump_reg()

	print( rtc.info() )
	print( "=== operation start ===" )
	
	osf	= rtc.oscillator_stopped()
	print( "rtc.oscillator_stopped()\n  --> ", end = "" )
	print( osf )

	machine_rtc	= machine.RTC()
	
	print( "== now ==" )
	print( "machine.rtc = {}".format( machine_rtc.now() ) )
	print( "PCF86263A   = {}".format( rtc.now() ) )
	
	print( "== datetime ==" )
	print( "machine.rtc = {}".format( machine_rtc.datetime() ) )
	print( "PCF86263A   = {}".format( rtc.datetime() ) )

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
	print( "rtc.init( ( 2017, 9, 14 )\n --> ", end = "" )
	print( rtc.datetime() )

	rtc.deinit()
	print( "rtc.deinit()\n --> ", end = "" )
	print( rtc.datetime() )

	rtc.datetime( (2022, 12, 21, 3, 21, 23, 32, 99) )
	print( "rtc.datetime( (2022, 12, 21, 3, 21, 23, 32, 99) )\n --> ", end = "" )
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

	intA	= Pin( "D2", Pin.IN )
	intA.irq( trigger = Pin.IRQ_FALLING, handler = callback )
	
	#intB	= Pin( "D3", Pin.IN, Pin.PULL_UP )
	#intB.irq( trigger = Pin.IRQ_FALLING, handler = callback )
	
	rtc.periodic_interrupt( pin_select = "A", period = 1 )

	alm	= rtc.timer_alarm( pin_select = "A", seconds = 5 )
	print( "alarm is set = {}".format( ", ".join( alm ) ) )

	pin4_as_timestamp_input( rtc )
	rtc.set_timestamp_interrupt( 1, pin_select = "B" )

	while True:
		if int_flag:
			event	= rtc.interrupt_clear()
			int_flag	= False

			event	= rtc.check_events( event )
			
			dt	= rtc.datetime()
			
			for e in event:
				print( "== event: {} {}".format( e, dt ), end = "     \r" if e == "periodic" else "     \n" )
	
				if not dt[ 6 ] % 30:
					rtc.dump_reg()

			if "alarm1" in event:
				print( "!!!!!!! ALARM !!!!!!!" )
				alm	= rtc.timer_alarm( seconds = 5 )
				print( "new alarm seting = {}".format( ", ".join( alm ) ) )

			if "timestamp1" in event:
				tsl	= rtc.timestamp()
				print( rtc.timestamp2str( tsl ) )


def pin4_as_timestamp_input( rtc ):
	intB	= Pin( "D3", Pin.IN, Pin.PULL_UP )	#	set pull-up at MCU side
	rtc.bit_operation( "Pin_IO", 0x7C, 0x7C )	#	pin4 of PCF85263A as TS input

if __name__ == "__main__":
	main()

