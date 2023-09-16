from	machine		import	I2C
from	utime		import	sleep	
from	nxp_periph	import	PCA8561

i2c		= I2C( 0, freq = (400 * 1000) )
lcd	= PCA8561( i2c )

lcd.puts( "NXP" )
sleep( 1 )

while True:
	for i in range( 10000 ):
		lcd.puts( f"{i:4}" )
