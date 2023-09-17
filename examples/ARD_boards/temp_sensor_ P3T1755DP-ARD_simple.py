###	Since the P3T1755DP-ARD board I2C signals are not assigned to A4 and A5 pin,
### a separate sample code made.
### The Software I2C is used because hardware I2C is available on A4&A5 and D0&D1
### pins on IMXRT1050-EVKB

from machine import SoftI2C
from utime import sleep
from nxp_periph import P3T1755

i2c = SoftI2C(sda="D14", scl="D15", freq=(400_000))
temp_sensor = P3T1755(i2c)

print(temp_sensor.info())

while True:
    value = temp_sensor.temp
    print(value)
    sleep(1)
