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
	
	for m in mtrs:
		print( "start CW: " + m.info() )
		m.start()
		sleep( 0.5 )

	mtrs[ 0 ].steps( 48 )
	mtrs[ 0 ].start()
	sleep( 1 )

	mtrs[ 0 ].steps( 96 )
	mtrs[ 1 ].steps( 48, reverse = True )
	mtrs[ 2 ].steps( 48 )
	mtrs[ 3 ].steps( 48, reverse = True )
	mtrs[ 4 ].steps( 96 )

	all_mtr.pps( 192 )
	all_mtr.pps( 192, reverse = True )
	
	while True:
		mtrs[ 0 ].start()
		sleep( 0.5 )
		mtrs[ 1 ].start( reverse = True )
		sleep( 0.25 )
		mtrs[ 2 ].start()
		sleep( 0.25 )
		mtrs[ 3 ].start( reverse = True )
		sleep( 0.25 )
		mtrs[ 4 ].start()
		sleep( 0.5 )
		mtrs[ 3 ].start( reverse = True )
		sleep( 0.25 )
		mtrs[ 2 ].start()
		sleep( 0.25 )
		mtrs[ 1 ].start( reverse = True )
		sleep( 0.25 )
		

if __name__ == "__main__":
	main()
