from	machine		import	I2C
from	utime		import	sleep
from	nxp_periph	import	PCA9629A

def main():
	INTERVAL	= 2
	
	i2c		= I2C( 0, freq = (400 * 1000) )
	mtr		= PCA9629A( i2c )

	print( "motor stop" )
	mtr.stop()

	print( "go home position" )
	mtr.home()
	sleep( INTERVAL )

	mtr.drv_phase( 0.5 )	# 0.5 = half_step, 1 = 1_phase, 2 = 2_phase

	mtr.steps( 192 )
	mtr.steps( 96, reverse = True )
	
	mtr.pps( 192 )
	mtr.pps( 96, reverse = True )

	print( "start CW" )
	mtr.start()
	sleep( INTERVAL )

	print( "start CCW" )
	mtr.start( reverse = True )
	sleep( INTERVAL )

	print( "start CW" )
	mtr.start()
	sleep( INTERVAL )

	print( "start CCW" )
	mtr.start( reverse = True )
	sleep( INTERVAL )

if __name__ == "__main__":
	main()
