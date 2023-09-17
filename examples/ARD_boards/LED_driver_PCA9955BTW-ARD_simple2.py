from machine import Pin, I2C
from utime import sleep_ms
from nxp_periph import PCA9955B

IREF_INIT = 0xFF

i2c = I2C(0, freq=(400 * 1000))
led_c = PCA9955B(i2c, address=0xBC >> 1, iref=IREF_INIT, setup_EVB=True)

print(led_c.info())
led_c.dump_reg()

while True:
    for i in range(16):
        for b in range(256):
            led_c.pwm(i, b)
            sleep_ms(3)
        for b in range(255, -1, -1):
            led_c.pwm(i, b)
            sleep_ms(3)
