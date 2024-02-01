###	Since the P3T1755DP-ARD board I2C signals are not assigned to A4 and A5 pin,
### a separate sample code made.

from machine import I2C, SoftI2C
from utime import sleep
from nxp_periph import P3T1755
import os

if "i.MX RT1050 EVKB-A" in os.uname().machine:
	i2c = SoftI2C(sda="D14", scl="D15", freq=(400_000))
else:
	i2c = I2C(0, freq=(400 * 1000))

temp_sensor = P3T1755(i2c)

print(temp_sensor.info())

while True:
    value = temp_sensor.temp
    print(value)
    sleep(1)
