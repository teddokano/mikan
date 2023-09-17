from machine import Pin, I2C
from utime import sleep
from nxp_periph import PCA9955B

i2c = I2C(0, freq=(400 * 1000))
led_c = PCA9955B(i2c, address=0xBC >> 1, setup_EVB=True)

print(led_c.info())
led_c.dump_reg()

while True:
    led_c.pwm(0, 0.5)
    sleep(0.1)
    led_c.pwm(0, 0.0)
    sleep(0.1)
