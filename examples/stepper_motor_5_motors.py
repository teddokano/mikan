from	machine		import	I2C
from	utime		import	sleep
from	nxp_periph	import	PCA9629A

def main():
	INTERVAL	= 2
	
	i2c			= I2C( 0, freq = (400 * 1000) )

	mtrs		= [	PCA9629A( i2c, address = 0x40 >> 1 ),
					PCA9629A( i2c, address = 0x42 >> 1 ), 
					PCA9629A( i2c, address = 0x44 >> 1 ),
					PCA9629A( i2c, address = 0x46 >> 1 ),
					PCA9629A( i2c, address = 0x48 >> 1 )
					]

	all_mtr		= PCA9629A( i2c, address = 0xE0 >> 1 )

	print( "motor stop" )
	all_mtr.stop()

	print( "go home position" )
	all_mtr.home()
	sleep( INTERVAL )

	all_mtr.drv_phase( 0.5 )	# 0.5 = half_step, 1 = 1_phase, 2 = 2_phase

	all_mtr.steps( 192 )
	all_mtr.steps( 96, reverse = True )

	all_mtr.pps( 192 )
	all_mtr.pps( 96, reverse = True )
	
	print( "start CW" )
	for m in mtrs:
		m.start()
		sleep( 0.5 )

	print( "start CCW" )
	for m in mtrs:
		m.start( reverse = True )
		sleep( 0.5 )

	print( "start CW" )
	for m in mtrs:
		m.start()
		sleep( 0.5 )

	print( "start CCW" )
	for m in mtrs:
		m.start( reverse = True )
		sleep( 0.5 )

if __name__ == "__main__":
	main()
