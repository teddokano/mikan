from	machine		import	I2C
from	nxp_periph	import	PCA8561

i2c		= I2C( 0, freq = (400 * 1000) )
lcd	= PCA8561( i2c )

lcd.puts( "TEST" )
