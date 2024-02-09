from machine import Pin, I2C, Timer
from nxp_periph import PCF85053A, MikanUtil
import machine
from utime import sleep

def main():
    intf = I2C(0, freq=(400 * 1000))
    rtc = PCF85053A(intf)

    print(rtc.info())
    print("=== operation start ===")

    #   Set read/write access right to primary I2C bus
    rtc.bit_operation( "Control_Register", 0x01, 0x01 )

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
    alarm_flag = False
    timer_flag = False

    def alarm_callback(pin_obj):
        nonlocal alarm_flag
        rtc.interrupt_clear()
        alarm_flag	= True

    def timer_callback(_):
        nonlocal timer_flag
        timer_flag	= True

    rtc.interrupt_clear()

    intr = Pin("D2", Pin.IN)
    intr.irq(trigger=Pin.IRQ_FALLING, handler=alarm_callback)

    t0 = Timer(MikanUtil.get_timer_id(0))
    t0.init(freq=1, mode=Timer.PERIODIC, callback=timer_callback)

    rtc.timer_alarm( seconds = 5 )

    while True:
        if alarm_flag:
            alarm_flag	= False
            rtc.timer_alarm(seconds=5)
            print("!!!!!!! ALARM !!!!!!!  alarm is set 5 seconds later")
		
        if timer_flag:
            timer_flag	= False
            dt	= rtc.datetime()
            print( dt )
		
if __name__ == "__main__":
    main()
