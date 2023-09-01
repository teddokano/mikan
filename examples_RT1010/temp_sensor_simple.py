from	machine		import	Pin, I2C, SoftI2C
from	utime		import	sleep

if "i.MX RT1010 EVK" in os.uname().machine:
	from	nxp_periph.temp_sensor	import	LM75B, PCT2075
else:
	from	nxp_periph	import	LM75B, PCT2075

def main():
	if "i.MX RT1010 EVK" in os.uname().machine:
		i2c		= I2C( 0, freq = (400 * 1000) )
	else:
		pass
				
#	temp_sensor	= PCT2075( i2c )
	temp_sensor	= LM75B( i2c, 76 )

	print( temp_sensor.info() )

	while True:
		value	= temp_sensor.temp
		print( value )
		sleep( 1 )

if __name__ == "__main__":
	main()
