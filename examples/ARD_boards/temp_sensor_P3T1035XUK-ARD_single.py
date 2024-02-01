from machine import I2C, SoftI2C
from utime import sleep
from nxp_periph import P3T1035
import os

if "i.MX RT1050 EVKB-A" in os.uname().machine:
	i2c = SoftI2C(sda="D14", scl="D15", freq=(400_000))
else:
	i2c = I2C(0, freq=(400 * 1000))

temp_sensor = P3T1035( i2c )
print(temp_sensor.info())

mid	= temp_sensor.reg_access("MID")
print( f"Manufacturer ID = 0x{mid:04X}" )

while True:
    value = temp_sensor.temp
    print(value)
    sleep(1)
