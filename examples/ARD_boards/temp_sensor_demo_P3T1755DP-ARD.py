from machine import Pin, I2C, SoftI2C, Timer
from nxp_periph import P3T1755, MikanUtil
import os


def main():
    int_flag = False
    tim_flag = False

    def callback(pin_obj):
        nonlocal int_flag
        int_flag = True

    def tim_cb(tim_obj):
        nonlocal tim_flag
        tim_flag = True

    int = Pin("D9", Pin.IN)
    int.irq(trigger=Pin.IRQ_FALLING, handler=callback)

    if "i.MX RT1050 EVKB-A" in os.uname().machine:
        i2c = SoftI2C(sda="D14", scl="D15", freq=(400_000))
    else:
        i2c = I2C(0, freq=(400 * 1000))

    temp_sensor = P3T1755(i2c)

    print(temp_sensor.info())
    temp_sensor.dump_reg()

    current_temp = temp_sensor.read()
    print(f"current temp = {current_temp}")
    t_hys, t_ots = temp_sensor.temp_setting([current_temp + 1, current_temp + 2])
    conf = temp_sensor.reg_access("Conf")
    temp_sensor.reg_access("Conf", conf | 0x0A)
    temp_sensor.dump_reg()

    tim0 = Timer(MikanUtil.get_timer_id(0))
    tim0.init(period=1000, callback=tim_cb)

    while True:
        if int_flag:
            int_flag = False
            v = temp_sensor.read()
            print("*** interrupt ***")

        if tim_flag:
            tim_flag = False
            value = temp_sensor.temp
            print(f"{value:.3f} deg-C   Tots/Thys setting: {t_ots:.1f}/{t_hys:.1f}")


if __name__ == "__main__":
    main()
