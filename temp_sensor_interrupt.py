from	machine		import	Pin, I2C, Timer
from	nxp_periph	import	PCT2075

def main():
	int_flag	= False
	tim_flag	= False

	def callback( pin_obj ):
		nonlocal	int_flag
		int_flag	= True
		
	def tim_cb( tim_obj ):
		nonlocal	tim_flag
		tim_flag	= True
		
	int	= Pin( "D2", Pin.IN )
	int.irq( trigger = Pin.IRQ_FALLING, handler = callback )

	i2c			= I2C( 0, freq = (400 * 1000) )
	temp_sensor	= PCT2075( i2c )

	temp_sensor.dump_reg()

	current_temp	= temp_sensor.read()
	thresholds		= temp_sensor.temp_setting( [ current_temp + 1.5, current_temp +0.5 ] )
	t_hys	= thresholds[ 0 ]
	t_ots	= thresholds[ 1 ]
	temp_sensor.bit_operation( "Conf", 0x02, 0x02 )

	#	The PCT2075DP-ARB (Arduino type evaluation board) has an on-board heater (R19 resister)
	#	The heater can be controlled by D3-pin

	heater	= Pin( "D3", Pin.OUT )	#	R19 as heater
	heater_on	= True
	heater.value( heater_on )

	temp_sensor.dump_reg()
	
	tim0 = Timer(0)
	tim0.init( period= 1000, callback = tim_cb)

	while True:
		if int_flag:
			int_flag	= False
			v	= temp_sensor.read()
			
			heater_on	= False if t_ots <= v else True
			heater.value( heater_on )

			print( "interrupt: heater is turned-{}".format( "ON" if heater_on else "OFF" ) )
			
		if tim_flag:
			tim_flag	= False
			value	= temp_sensor.read()
			print( "{:.3f} deg-C   Tots/Thys setting: {:.1f}/{:.1f}   on-board heater {}".format( value, t_ots, t_hys, "ON" if heater_on else "OFF" ) )
			#sleep( 1.0 )


if __name__ == "__main__":
	main()
