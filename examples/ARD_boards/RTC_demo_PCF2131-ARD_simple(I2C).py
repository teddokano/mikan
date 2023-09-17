import machine
from machine import I2C, SPI
from utime import sleep
from nxp_periph import PCF2131, RTC_base

intf = I2C(0, freq=(400 * 1000))
# intf	= SPI( 0, 500 * 1000, cs = 0 )
rtc = PCF2131(intf)

machine_rtc = machine.RTC()

print(rtc.info())
print("=== operation start ===")

osf = rtc.oscillator_stopped()
print(f"rtc.oscillator_stopped()  --> {osf}")

if osf:
    rtc.datetime(machine_rtc.datetime())
    print("current time copied from PC into PCF2131")

while True:
    print(rtc.now())
    sleep(1)
