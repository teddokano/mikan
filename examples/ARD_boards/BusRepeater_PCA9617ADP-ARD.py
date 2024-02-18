from machine import I2C
from utime import sleep
from nxp_periph import M24C02
from nxp_periph import BusInOut

i2c = I2C(0, freq=(400_000))
eeprom = M24C02(i2c)

ldo1 = BusInOut(["D3", "D4", "D5"])
ldo2 = BusInOut(["D1", "D2"])
ldo1.output()
ldo2.output()

v1_values = [0.8, 1.8, 2.5, 3.3, 4.96]
v2_values = [2.5, 3.0, 3.3, 4.96]

print(eeprom.info())

str0 = "Hello, PCA9716A! This is a demo code for the BusRepeater_PCA9617ADP-ARD board."
str1 = (
    "This demo code is write and read EEPROM through PCA9617A with different voltages."
)

while True:
    for v1 in range(5):
        for v2 in range(4):
            if (v1 == 3) and (v2 == 0):
                continue

            ldo1.v = v1
            ldo2.v = v2

            print(
                "New voltages are set: LDO1 = {}V, LDO2 = {}V".format(
                    v1_values[v1], v2_values[v2]
                )
            )
            sleep(1)

            eeprom.write(0, str0)
            print(eeprom.read(0, len(str0), format="str"))

            eeprom.write(0, str1)
            print(eeprom.read(0, len(str1), format="str"))
            print("")
