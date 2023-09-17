from machine import Pin, I2C, SPI
from nxp_periph import PCF2131, RTC_base
import machine

BAT_SWOVR = True


def feature_test(rtc):
    print("\nDate&Time register operation test:")

    print("rtc.datetime()\n --> ", end="")
    print(rtc.datetime())

    rtc.init((2017, 9, 14))
    print("rtc.init( ( 2017, 9, 14 )\n --> ", end="")
    print(rtc.datetime())

    rtc.deinit()
    print("rtc.deinit()\n --> ", end="")
    print(rtc.datetime())

    rtc.datetime((2022, 12, 21, 3, 21, 23, 32, 99))
    print("rtc.datetime( (2022, 12, 21, 3, 21, 23, 32, 99) )\n --> ", end="")
    print(rtc.datetime())

    print("rtc.now()\n --> ", end="")
    print(rtc.now())

    print("")


def demo(rtc):
    int_flag = False

    def callback(pin_obj):
        nonlocal int_flag
        int_flag = True

    rtc.interrupt_clear()

    intA = Pin("D8", Pin.IN)
    intA.irq(trigger=Pin.IRQ_FALLING, handler=callback)

    intB = Pin("D9", Pin.IN)
    intB.irq(trigger=Pin.IRQ_FALLING, handler=callback)

    rtc.periodic_interrupt(pin_select="A", period=1)

    alm = rtc.timer_alarm(pin_select="B", seconds=5)
    print("alarm is set = {}".format(", ".join(alm)))

    rtc.set_timestamp_interrupt(1, pin_select="B")

    while True:
        if int_flag:
            event = rtc.interrupt_clear()
            int_flag = False

            event = rtc.check_events(event)

            dt = rtc.datetime()

            for e in event:
                print(
                    "{} {}".format(e, dt),
                    end="     \n" if e is "periodic" else "     \n",
                )

            if "alarm" in event:
                print("!!!!!!! ALARM !!!!!!!")
                alm = rtc.timer_alarm(seconds=5)
                print("new alarm seting = {}".format(", ".join(alm)))

            if "ts1" in event:
                tsl = rtc.timestamp()
                print(rtc.timestamp2str(tsl))

            if not dt[6] % 30:
                rtc.dump_reg()


# intf	= I2C( 0, freq = (400 * 1000) )
intf = SPI(0, 500 * 1000, cs=0)
rtc = PCF2131(intf)

print(rtc.info())
print("=== operation start ===")

osf = rtc.oscillator_stopped()
print("rtc.oscillator_stopped()\n  --> ", end="")
print(osf)

rtc.battery_switchover(BAT_SWOVR)

machine_rtc = machine.RTC()

print("== now ==")
print("machine.rtc = {}".format(machine_rtc.now()))
print("PCF2131     = {}".format(rtc.now()))

print("== datetime ==")
print("machine.rtc = {}".format(machine_rtc.datetime()))
print("PCF2131     = {}".format(rtc.datetime()))

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
