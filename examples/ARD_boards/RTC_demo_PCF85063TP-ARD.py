from machine import Pin, I2C
from nxp_periph import PCF85063TP
from utime import sleep
import machine


def main():
    intf = I2C(0, freq=(400 * 1000))
    rtc = PCF85063TP(intf)

    print(rtc.info())
    print("=== operation start ===")

    osf = rtc.oscillator_stopped()
    print("rtc.oscillator_stopped()\n  --> ", end="")
    print(osf)

    machine_rtc = machine.RTC()
    if osf:
        source, target, msg = machine_rtc, rtc, "stop is detected"
        feature_test(rtc)
    else:
        source, target, msg = rtc, machine_rtc, "was kept running"

    target.datetime(source.datetime())
    print(
        "since RTC device oscillator {}, Date&Time symchronized : {} --> {}".format(
            msg, source, target
        )
    )

    print("rtc.now()\n --> ", end="")
    print(rtc.now())

    demo(rtc)


def feature_test(rtc):
    print("\nDate&Time register operation test:")

    print("rtc.datetime()\n --> ", end="")
    print(rtc.datetime())

    rtc.init((2017, 9, 14))
    print("tc.init( ( 2017, 9, 14 )\n --> ", end="")
    print(rtc.datetime())

    rtc.deinit()
    print("rtc.deinit()\n --> ", end="")
    print(rtc.datetime())

    rtc.datetime((2022, 12, 21, 21, 23, 32, 99, None), 1)
    print("rtc.datetime( (2022, 12, 21, 21, 23, 32, 99, None ), 1 )\n --> ", end="")
    print(rtc.datetime())

    print("rtc.now()\n --> ", end="")
    print(rtc.now())

    print("")


def demo(rtc):
    while True:
        dt = rtc.datetime()
        print(dt)
        sleep(1)


if __name__ == "__main__":
    main()
