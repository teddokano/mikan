from nxp_periph		import	FXOS8700
from machine		import	I2C
from utime			import	sleep

import	math

def main():
	i2c		= I2C( 0, freq = (400 * 1000) )
	acc		= FXOS8700( i2c )

	print( 	i2c.scan() )
	acc.dump_reg()

	xc, yc	= -74400.0, -78850

#	xc, yc	= calibration( acc )

	while True:
		x, y, _	= acc.mag()
		deg	= math.atan2( y - yc, x - xc ) / math.pi * 180
#		deg	= deg + 360 if deg < 0 else deg
		print( deg )
		sleep( 0.2 )

def calibration( acc ):
	print( "calibration for 10 seconds: rotate the board on X-Y plane" )
	
	xs	= []
	ys	= []
	
	for i in range( 100 ):
		print( "{} seconds".format( i / 10 ), end = "\r" )
		x, y, _	= acc.mag()
		xs	+= [ x ]
		ys	+= [ y ]
		sleep( 0.1 )

	print( "calibration done" )
	xc	= (max( xs ) - min( xs )) / 2 + min( xs )
	yc	= (max( ys ) - min( ys )) / 2 + min( ys )

	print( max( xs ), min( xs ), xc )
	print( max( ys ), min( ys ), yc )
	
	return xc, yc

if __name__ == "__main__":
	main()
