from machine import Pin, I2C, Timer
from nxp_periph import PCT2075, MikanUtil


def main():
    int_flag = False
    tim_flag = False

    def callback(pin_obj):
        nonlocal int_flag
        int_flag = True

    def tim_cb(tim_obj):
        nonlocal tim_flag
        tim_flag = True

    int = Pin("D2", Pin.IN)
    int.irq(trigger=Pin.IRQ_FALLING, handler=callback)

    i2c = I2C(0, freq=(400 * 1000))

    # 	The PCT2075DP-ARB (Arduino type evaluation board) has an on-board heater (R19 resister)
    # 	The heater can be controlled by D3-pin
    # 	This instance declaration with "setup_EVB = True" enables to use the heater with "PCT2075.heater"
    temp_sensor = PCT2075(i2c, setup_EVB=True)

    print(temp_sensor.info())
    temp_sensor.dump_reg()

    current_temp = temp_sensor.read()
    thresholds = temp_sensor.temp_setting([current_temp + 1.5, current_temp + 0.5])
    t_hys = thresholds[0]
    t_ots = thresholds[1]
    temp_sensor.bit_operation("Conf", 0x02, 0x02)

    temp_sensor.dump_reg()
    temp_sensor.heater = True

    tim0 = Timer(MikanUtil.get_timer_id(0))
    tim0.init(period=1000, callback=tim_cb)

    while True:
        if int_flag:
            int_flag = False
            v = temp_sensor.read()

            temp_sensor.heater = False if t_ots <= v else True

            print(
                "interrupt: heater is turned-{}".format(
                    "ON" if temp_sensor.heater else "OFF"
                )
            )

        if tim_flag:
            tim_flag = False
            value = temp_sensor.temp
            print(
                "{:.3f} deg-C   Tots/Thys setting: {:.1f}/{:.1f}   on-board heater {}".format(
                    value, t_ots, t_hys, "ON" if temp_sensor.heater else "OFF"
                )
            )
            # sleep( 1.0 )


if __name__ == "__main__":
    main()
