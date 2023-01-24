from	machine		import	Pin, SoftI2C, Timer
from	nxp_periph	import	P3T1085

def main():
	int_flag	= False
	tim_flag	= False

	def callback( pin_obj ):
		nonlocal	int_flag
		temp_sensor.reg_access( "Conf" )	#	to clear INT
		int_flag	= True
		
	def tim_cb( tim_obj ):
		nonlocal	tim_flag
		tim_flag	= True
		
	int	= Pin( "D8", Pin.IN )
	int.irq( trigger = Pin.IRQ_FALLING, handler = callback )

	i2c	= SoftI2C( sda = "D14", scl = "D15", freq = (400 * 1000) )
	temp_sensor	= P3T1085( i2c )

	print( temp_sensor.info() )
	temp_sensor.dump_reg()

	current_temp	= temp_sensor.read()
	thresholds		= temp_sensor.temp_setting( [ current_temp + 2.5, current_temp -2.5 ] )
	t_hys	= thresholds[ 0 ]
	t_ots	= thresholds[ 1 ]
	conf	= temp_sensor.reg_access( "Conf" )
	temp_sensor.reg_access( "Conf", conf | 0x0400 )
	temp_sensor.dump_reg()

	tim0 = Timer(0)
	tim0.init( period= 1000, callback = tim_cb)

	while True:
		if int_flag:
			int_flag	= False
			v	= temp_sensor.read()
			
			print( "*** interrupt ***" )
			
		if tim_flag:
			tim_flag	= False
			value	= temp_sensor.temp
			print( "{:.3f} deg-C   Tots/Thys setting: {:.1f}/{:.1f}".format( value, t_ots, t_hys ) )
	
if __name__ == "__main__":
	main()
