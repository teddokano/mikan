from machine import I2C, SoftI2C
from utime import sleep
from nxp_periph import P3T1035, P3T2030
import os

if "i.MX RT1050 EVKB-A" in os.uname().machine:
    i2c = SoftI2C(sda="D14", scl="D15", freq=(400_000))
else:
    i2c = I2C(0, freq=(400 * 1000))

chars = tuple(chr(c) for c in range(ord("A"), ord("A") + 8))
print(chars)

temp_sensors = []

for addr in range(0xE0, 0xF0, 2):
    temp_sensors += [P3T1035(i2c, 0x98 >> 1)]
# 	temp_sensors	+= [ P3T2030( i2c, 0x98 >> 1 ) ]

for ts in temp_sensors:
    print(ts.info())


for c in chars:
    print(f"|{c:_<7}", end="")

print("")

while True:
    for ts in temp_sensors:
        print(f" {ts.temp:7.3f}", end="")

    print("")

    sleep(1)
