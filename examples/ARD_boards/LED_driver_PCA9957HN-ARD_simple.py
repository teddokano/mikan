from machine import Pin, SPI
from utime import sleep
from nxp_periph import PCA9957

spi		= SPI( 0, 1000 * 1000, cs = 0 )
led_c	= PCA9957( spi, setup_EVB = True )

print(led_c.info())
led_c.dump_reg()

while True:
    led_c.pwm(0, 0.5)
    sleep(0.1)
    led_c.pwm(0, 0.0)
    sleep(0.1)
