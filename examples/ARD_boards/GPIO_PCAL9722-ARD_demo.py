from machine import Pin, SPI, Timer
from nxp_periph import PCAL9722, MikanUtil
from utime import sleep


def main():
    int_flag = False
    tim_flag = False

    def callback(pin_obj):
        nonlocal int_flag
        int_flag = True

    def tim_cb(tim_obj):
        nonlocal tim_flag
        tim_flag = True

    int_pin = Pin("D7", Pin.IN)
    int_pin.irq(trigger=Pin.IRQ_FALLING, handler=callback)

    spi = SPI(0, 1000 * 1000, cs=0)
    gpio = PCAL9722(spi, setup_EVB=True)

    io_config_and_pull_up = [0x00, 0x00, 0x3F]

    gpio.config = io_config_and_pull_up
    gpio.pull_up = io_config_and_pull_up
    gpio.mask = [~v for v in io_config_and_pull_up]
    gpio.pull_en = [0xFF] * gpio.__np

    tim0 = Timer(MikanUtil.get_timer_id(0))
    tim0.init(period=10, callback=tim_cb)

    count = 0

    led_length = len(led)

    m = Message("  Hello PCAL9722 SPI GPIO Expander")

    while True:
        if int_flag:
            int_flag = False
            status = gpio.status
            value = gpio.value
            print("\n--- inetrupt:")
            print(
                "  Interrupt status = {}".format(["0b{:08b}".format(i) for i in status])
            )
            print("  Input Port	   = {}".format(["0b{:08b}".format(i) for i in value]))

            m.button_press(status[2])
            count = -20

        if tim_flag:
            tim_flag = False
            gpio.value = [led[count % led_length]] + [m.char(count)]

            count += 1

            r = gpio.value

            print("port read = {}".format(["0b{:08b}".format(i) for i in r]), end="\r")

        sleep(0.05)


class Message:
    pat = (
        0xC0, 0xF9, 0xA4, 0xB0, 0x99, 0x92, 0x82, 0xF8,  # 	0~7
        0x80, 0x90, 0x88, 0x83, 0xC6, 0xA1, 0x86, 0x8E,  # 	8~F
        0xC2, 0x89, 0xCF, 0xF1, 0x8D, 0xC7, 0xAA, 0xAB,  # 	G~N
        0xA3, 0x8C, 0x98, 0xAF, 0x92, 0x87, 0xE3, 0xC1,  # 	O~V
        0xE2, 0x9B, 0x91, 0xB6,  # 	W~Z
    )

    def __init__(self, s):
        self.s = s
        self.p = 0
        self.l = len(s)

    def char(self, t):
        if t < 0:
            c = self.button
        else:
            if not (t & 0x7):
                return 0xFF

            p = (t >> 3) % self.l
            c = self.s[p]

        if c == ".":
            return 0x7F
        elif c.isupper():
            return self.pat[ord(c) - ord("A") + 10]
        elif c.islower():
            return self.pat[ord(c) - ord("a") + 10]
        elif c.isdigit():
            return self.pat[ord(c) - ord("0")]

        return 0xFF

    def button_press(self, v):
        self.button = chr(self.find_bit(v) + ord("0"))

    def find_bit(self, v):
        for i in range(6):
            if (v >> i) & 0x1:
                return i


led = ( 0xFE, 0xFD, 0xFB, 0xF7, 0xEF, 0xDF, 0xBF, 0x7F, 0xBF, 0xDF, 0xEF, 0xF7, 0xFB, 0xFD )

if __name__ == "__main__":
    main()
