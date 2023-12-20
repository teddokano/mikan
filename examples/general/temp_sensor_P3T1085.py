###	Since the P3T1085UK-ARD board I2C signals are not assigned to A4 and A5 pin, 
### a separate sample code made.
### The Software I2C is used because hardware I2C is available on A4&A5 and D0&D1
### pins on IMXRT1050-EVKB

from	machine		import	I2C, SoftI2C
from	utime		import	sleep
from	nxp_periph	import	P3T1085
import	os

def main():
	if "i.MX RT1050 EVKB-A" in os.uname().machine:
		i2c = SoftI2C(sda="D14", scl="D15", freq=(400_000))
	else:
		i2c = I2C(0, freq=(400 * 1000))

	temp_sensor	= P3T1085( i2c )

	print( temp_sensor.info() )

	thresholds		= temp_sensor.temp_setting( [ 33.5, 10 ] )

	while True:
		value	= temp_sensor.temp
		print( value )
		sleep( 1 )

if __name__ == "__main__":
	main()
