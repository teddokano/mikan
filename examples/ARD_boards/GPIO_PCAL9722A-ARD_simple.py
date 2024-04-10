from machine import SPI
from nxp_periph import PCAL9722
from utime import sleep

spi = SPI(0, 1000 * 1000, cs=0)
gpio = PCAL9722(spi, setup_EVB=True)

io_config_and_pull_up = [0x00, 0x00, 0x3F]

gpio.config = io_config_and_pull_up
gpio.pull_up = io_config_and_pull_up
gpio.mask = [~v for v in io_config_and_pull_up]
gpio.pull_en = [0xFF] * gpio.__np

count = 0

while True:
    gpio.value = [(0xFF << count % 9)] + [~(0x1 << count % 6)]
    count += 1

    r = gpio.value
    print("port read = {}".format(["0b{:08b}".format(i) for i in r]), end="\r")

    sleep(0.1)
