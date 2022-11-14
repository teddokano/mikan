from	machine		import	I2C
from	utime		import	sleep
from	nxp_periph	import	PCA9629A

def main():
	i2c		= I2C( 0, freq = (400 * 1000) )
	mtr		= PCA9629A( i2c )
	all_mtr	= PCA9629A( i2c, address = 0xE0 >> 1 )	#	Allcall address

	mtr.stop()
	all_mtr.home()
	sleep( 1 )

	all_mtr.drv_phase( 0.5 )
	all_mtr.dump_reg()

	mtr.steps( 192 )
	mtr.steps( 96, reverse = True )
	mtr.pps( 192 )
	mtr.pps( 96, reverse = True )
	mtr.start()
	sleep( 2.1 )
	mtr.start( reverse = True )

if __name__ == "__main__":
	main()
