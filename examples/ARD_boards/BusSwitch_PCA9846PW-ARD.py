from machine import I2C
from utime import sleep
from nxp_periph import PCA9846, M24C02


i2c = I2C(0, freq=400_000)
sw = PCA9846(i2c)

eeproms = [
    M24C02(i2c, 0xA0 >> 1),
    M24C02(i2c, 0xA2 >> 1),
    M24C02(i2c, 0xA4 >> 1),
    M24C02(i2c, 0xA6 >> 1),
]

sw.select(PCA9846.CH3 | PCA9846.CH2 | PCA9846.CH1 | PCA9846.CH0)

### Select all channels and write each EEPROM

for i, e in enumerate(eeproms):
    print(f"[eeprom in ch{i}] {e.info()}")
    length = e.write(
        0,
        f"[eeprom in ch{i}] Hello, BusSwitch PCA9846! This is a demo code for the BusSwitch_PCA9846PW-ARD board.",
    )

while True:

    ### Select all channels and read all EEPROMs

    sw.select(PCA9846.CH3 | PCA9846.CH2 | PCA9846.CH1 | PCA9846.CH0)
    print(f"\nall channels enabled (sw.select() → 0b{sw.select():04b}):")

    for i, e in enumerate(eeproms):
        if e.ping():  # Need to ping to re-enable the device which has been NACKed
            print(e.read(0, length, format="str"))

    sleep(1)

    ### Select one channel and try to read all EEPROMs

    for i in range(sw.N_CH):

        sw.select(0x01 << i)
        print(f"\nchannel {i} is enabled (sw.select() → 0b{sw.select():04b}):")

        for e in eeproms:
            if e.ping():
                print(e.read(0, length, format="str"))

        sleep(1)
