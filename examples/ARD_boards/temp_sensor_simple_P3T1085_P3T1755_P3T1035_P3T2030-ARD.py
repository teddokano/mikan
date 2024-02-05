###	Sample code for P3T1085, P3T1755, P3T1035, P3T2030 ARD boards.
### On those boards, I2C signals are not assigned to A4 and A5 pin.
### To use those boards on IMXRT1050-EVKA, need to use D14 and D15 pins
### with SoftI2C.
### IMXRT1050-EVK-B don't need this treatment because A4 and A5 pins
### are connected with D14 and D15 (hard wired)

from machine import I2C, SoftI2C
from utime import sleep
from nxp_periph import P3T1085, P3T1755, P3T1035, P3T2030
import os

if "i.MX RT1050 EVKB-A" in os.uname().machine:
    i2c = SoftI2C(sda="D14", scl="D15", freq=(400_000))
else:
    i2c = I2C(0, freq=(400 * 1000))

temp_sensor = P3T1085(i2c)
# temp_sensor	= P3T1755( i2c )
# temp_sensor	= P3T1035( i2c )
# temp_sensor	= P3T2030( i2c )

print(temp_sensor.info())

while True:
    value = temp_sensor.temp
    print(value)
    sleep(1)
