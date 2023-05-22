from	machine		import	Pin, I2C
from	utime		import	sleep
from	nxp_periph	import	PCT2075

temp_sensor	= PCT2075( I2C( 0 ) )

print( temp_sensor.info() )

while True:
	print( temp_sensor.temp )
	sleep( 1 )
