# "mikan" 💡⏰🌡️↕🔠🔄💁🍎🌊
I²C/SPI peripheral device driver for collection for MicroPython.  
_The name of this repository has been changed from "mp_driver" to "mikan" (2022 Nov 02)._


# What is this?
NXP peripheral device drivers (SDK) for [MicroPython](https://micropython.org) and its usage examples and demo.  
The drivers provided to operate I²C/SPI peripheral devices. It enables quick evaluation and rapid demo development by simple intuitive interface (API) and flexible MicroPython environment.  
Refer to YouTube video [(English version)](https://youtu.be/CEBe6YpOWSI), [(Japanese version)](https://youtu.be/WYQKIY8iBYM) to find what can be done.

![Boards](https://github.com/teddokano/additional_files/blob/main/mikan/img/boards.jpeg)  
_[Arduino® Shields Solutions](https://www.nxp.com/design/development-boards/analog-toolbox/arduino-shields-solutions:ARDUINO-SOLUTIONS) boards and I²C peripheral evaluation boards with 
[i.MX RT1050 Evaluation Kit](https://www.nxp.com/design/development-boards/i-mx-evaluation-and-development-boards/i-mx-rt1050-evaluation-kit:MIMXRT1050-EVK)_  
  
![example_operation](https://github.com/teddokano/additional_files/blob/main/mikan/img/example_operation.png)  
_Screen shot of ~~`examples/temp_sensor_interrupt.py`~~ [`examples/temp_sensor_demo_PCT2075DP_ARB.py`](https://github.com/teddokano/mikan/blob/main/examples/temp_sensor_demo_PCT2075DP_ARB.py) operation_
  
![remote_demo](https://github.com/teddokano/additional_files/blob/main/mikan/img/remote_demo.png)
_"[remote_demo](https://github.com/teddokano/mikan/tree/main/remote_demo)" running. Device operation can be done from web browser_
  
# Supported devices
- Real Time Clock (RTC)
	- [PCF2131](https://www.nxp.com/products/peripherals-and-logic/signal-chain/real-time-clocks/rtcs-with-temperature-compensation/nano-power-highly-accurate-rtc-with-integrated-quartz-crystal:PCF2131) (for both I²C and SPI interface can be used)
	- [PCF85063A](https://www.nxp.com/products/peripherals-and-logic/signal-chain/real-time-clocks/rtcs-with-ic-bus/tiny-real-time-clock-calendar-with-alarm-function-and-ic-bus:PCF85063A)
- Temperature sensor
	- [LM75B](https://www.nxp.com/products/sensors/ic-digital-temperature-sensors/digital-temperature-sensor-and-thermal-watchdog:LM75B)
	- [PCT2075](https://www.nxp.com/products/sensors/ic-digital-temperature-sensors/ic-bus-fm-plus-1-degree-c-accuracy-digital-temperature-sensor-and-thermal-watchdog:PCT2075)
	- [P3T1085](https://www.nxp.com/products/sensors/ic-digital-temperature-sensors/i3c-ic-bus-0-5-c-accurate-digital-temperature-sensor:P3T1085UK) (I²C operation)
	- [P3T1035](https://www.nxp.com/products/sensors/i3c-ic-digital-temp-sensors/i3c-ic-bus-0-5-c-accuracy-digital-temperature-sensor:P3T1035xUK) (I²C operation)
	- [P3T2030](https://www.nxp.com/products/sensors/i3c-ic-digital-temp-sensors/i3c-ic-bus-2-0-c-accuracy-digital-temperature-sensor:P3T2030xUK) (I²C operation)
- LED controller
	- [PCA9632](https://www.nxp.com/products/power-management/lighting-driver-and-controller-ics/led-controllers/4-bit-fm-plus-ic-bus-low-power-led-driver:PCA9632) (PCA9633 compatible)
	- [PCA9955B](https://www.nxp.com/products/power-management/lighting-driver-and-controller-ics/led-drivers/16-channel-fm-plus-ic-bus-57-ma-20-v-constant-current-led-driver:PCA9955BTW)
	- [PCA9956B](https://www.nxp.com/products/power-management/lighting-driver-and-controller-ics/led-drivers/24-channel-fm-plus-ic-bus-57-ma-20-v-constant-current-led-driver:PCA9956BTW)
	- [PCA9957](https://www.nxp.com/products/power-management/lighting-driver-and-controller-ics/led-drivers/24-channel-spi-serial-bus-32-ma-5-5-v-constant-current-led-driver:PCA9957)
- GPIO expander
	- [PCA9554](https://www.nxp.com/products/interfaces/ic-spi-i3c-interface-devices/general-purpose-i-o-gpio/8-bit-ic-bus-and-smbus-i-o-port-with-interrupt:PCA9554_PCA9554A) (PCA9554A, PCA9554B, PCA9554C, PCA9538 compatible)
	- [PCA9555](https://www.nxp.com/products/interfaces/ic-spi-i3c-interface-devices/general-purpose-i-o-gpio/16-bit-ic-bus-and-smbus-i-o-port-with-interrupt:PCA9555) (PCA9555A, PCA9539 compatible)
	- [PCAL6408](https://www.nxp.com/products/interfaces/ic-spi-i3c-interface-devices/general-purpose-i-o-gpio/low-voltage-translating-8-bit-ic-bus-smbus-i-o-expander:PCAL6408A)
	- [PCAL6416](https://www.nxp.com/products/interfaces/ic-spi-i3c-interface-devices/general-purpose-i-o-gpio/low-voltage-translating-16-bit-ic-bus-smbus-i-o-expander:PCAL6416A)
	- [PCAL6524](https://www.nxp.com/products/interfaces/ic-spi-i3c-interface-devices/ic-bus-controller-and-bridge-ics/ultra-low-voltage-translating-24-bit-fm-plus-ic-bus-smbus-i-o-expander:PCAL6524)
	- [PCAL6534](https://www.nxp.com/products/interfaces/ic-spi-i3c-interface-devices/general-purpose-i-o-gpio/ultra-low-voltage-level-translating-34-bit-ic-bus-smbus-i-o-expander:PCAL6534)
- LCD driver
	- [PCA8561](https://www.nxp.jp/products/peripherals-and-logic/lcd-drivers/lcd-segment-drivers/automotive-18-x-4-lcd-segment-driver:PCA8561)
- Protocol bridge
	- SC16IS7xx (
		[Single UART](https://www.nxp.com/products/peripherals-and-logic/signal-chain/bridges/single-uart-with-ic-bus-spi-interface-64-bs-of-transmit-and-receive-fifos-irda-sir-built-in-support:SC16IS740_750_760),
		[Dual UART](https://www.nxp.com/products/peripherals-and-logic/signal-chain/bridges/dual-uart-with-ic-bus-spi-interface-64-bs-of-transmit-and-receive-fifos-irda-sir-built-in-support:SC16IS752_SC16IS762)
		)
	- [SC18IS606](https://www.nxp.com/products/peripherals-and-logic/signal-chain/bridges/ic-bus-to-spi-bridge:SC18IS606)
- Stepper motor controller
	- [PCA9629A](https://www.nxp.com/products/interfaces/ic-spi-i3c-interface-devices/ic-bus-controller-and-bridge-ics/fm-plus-ic-bus-advanced-stepper-motor-controller:PCA9629APW)
- Accelerometer
	- [FXOS8700](https://www.nxp.com/docs/en/data-sheet/FXOS8700CQ.pdf)
	- [FXLS8974](https://www.nxp.jp/docs/en/data-sheet/FXLS8974CF.pdf)
- Analog Front-End
	- [NAFE13388](https://www.nxp.com/products/analog-and-mixed-signal/analog-front-end/highly-configurable-8-channel-25-v-universal-input-analog-front-end-with-excitation-sources:NAFEx3388)

# Getting started

## The steps

The instllation can be completed in 2 steps as follows.  

1. Step 1
	1. Install MicroPython into the MCU board (Follow instraction to MicroPython [download page](https://micropython.org/download/) for each MCU boards). 
1. Step 2
	1. Check sys.path (**module serch path**) on target board
		1. Connect your MCU board and PC, get REPL environment. When the [MIMXRT1050_EVK](https://www.nxp.com/design/development-boards/i-mx-evaluation-and-development-boards/i-mx-rt1050-evaluation-kit:MIMXRT1050-EVK) is connected to terminal, press 'Ctrl + b' keys to get prompt (exit from 'raw' mode). 
		1. Check path setting by typing.. 
		```
		>>> import sys
		>>> print(sys.path)
		```
		Then you will get list of path like (in case of the [MIMXRT1050_EVK](https://www.nxp.com/design/development-boards/i-mx-evaluation-and-development-boards/i-mx-rt1050-evaluation-kit:MIMXRT1050-EVK))
		```
		['', '.frozen', '/flash', '/flash/lib']
		```
		or  (in case of Raspberry Pi Pico)
		```
		['', '.frozen', '/lib']
		```
	1. Copy "nxp_periph" folder into target's' "lib" (it could be '/flash/lib' or '/lib') directory.  For file/folder copying, some tools can be used like [Thonny](https://thonny.org), [rshell](https://github.com/dhylands/rshell), etc.
	1. Now it's ready to play! Choose an example code in "example" folder and run.

### Video guide

Video guide is available which was explained above.  
Take following step1 and step2 to complete the installation. 

#### Step 1: Install MicroPython on the MCU board
Follow this video to install MicroPython into the MCU board. This is an example of i.MXRT1050-EVK.  
Use latest version of MicroPython: [**v1.22.0**](https://micropython.org/resources/firmware/MIMXRT1050_EVK-20231227-v1.22.0.bin).   
[https://youtu.be/L2AVKoXI4vI](https://youtu.be/L2AVKoXI4vI)  
[![](https://github.com/teddokano/additional_files/blob/main/mikan/img/mikan_install_step_1.png)](https://youtu.be/L2AVKoXI4vI)

#### Step 2: Install 'mikan' into the MCU board
Need to copy 'mikan' class driver into the MCU board storage. The guide video shows how to copy using Thonny. 
[https://youtu.be/rG8MwNkk9xs](https://youtu.be/rG8MwNkk9xs)  
[![](https://github.com/teddokano/additional_files/blob/main/mikan/img/mikan_install_step2.png)](https://youtu.be/rG8MwNkk9xs)

> **Note**  
> Install can be done with a package management tool called: [`mip`](https://docs.micropython.org/en/latest/reference/packages.html#installing-packages-with-mpremote).  
> It can be done with command of `mpremote mip install github:teddokano/mikan`.  
> Using `mpremote` is easy way to install the library. However it needs to setup the tool on your PC. So in this document, manual install steps described to do it in simple way. 



# What is inside?
## Drivers
The drivers are main part of this repo.  
The driver code files are in `nxp_periph/`.  
The drivers are provided as class-libraries with device names (type-numbers). With this class-libraries, the device operations are highly abstracted and simplified. Methods of the class-drivers enables major features of devices and and provides register level access for user custom operation. 

For example, for the LED controller (PCA9955B) ...
```python
from machine    import I2C      # Importing 'I²C' class library from MicroPython's 'machine' module
from utime      import sleep    # Importing 'sleep' from MicroPython's 'utime' module
from nxp_periph import PCA9955B # Importing the device class library of 'PCA9955B'

i2c   = I2C( 0, freq = (400 * 1000) ) # Making an instance of I²C with 400kHz clock setting
led_c = PCA9955B( i2c )               # Making an instance of PCA9955B which is connected to the 'i2c'.

while True:             # Looping following part forever
    led_c.pwm( 0, 0.5 ) # Letting PCA9955B channel 0 as 50% PWM output
    sleep( 0.1 )        # Waiting 0.1 second
    led_c.pwm( 0, 0.0 ) # Letting PCA9955B channel 0 as 50% PWM output
    sleep( 0.1 )        # Waiting 0.1 second
```

If register access is needed, `write_registers()` and `read_registers()` methods are available (for any devices). It takes register name or index/address as first argument.  
For `write_registers()` second argument is an integer or a list. When it is an integer, the value is written. If the list is given, the values in the list are wrtten into consecutive registers.  
For `read_registers()`, second argument specifies the number of bytes to read. If it is '1', method returns an integer value. If it is '>1', list will be returned. 
```python
led_c.write_registers( "LEDOUT0", [ 0xAA, 0xAA, 0xAA, 0xAA ] ) # example of four 0xAA writing into consecutive registers from "LEDOUT0"
```

Next sample is a temperature sensor operation. Simple interface enables just read the temperature in celcius.
```python
from machine    import I2C     # Importing 'I²C' class library from MicroPython's 'machine' module
from utime      import sleep   # Importing 'sleep' from MicroPython's 'utime' module
from nxp_periph import PCT2075 # Importing the device class library of 'PCT2075'

i2c         = I2C( 0, freq = (400 * 1000) ) # Making an instance of I²C with 400kHz clock setting
temp_sensor = PCT2075( i2c )                # Making an instance of PCT2075 which is connected to the 'i2c'.

while True:                    # Looping following part forever
    value   = temp_sensor.temp # Reading temperature in celsius value
    print( value )             # Showing the value
    sleep( 1 )                 # Waiting for 1 second
```

For more information of examples, please find next section of this document. 

## Examples
The example code files are in `examples/general/` folder.  
It shows simple usage examples for the drivers and standalome demo for target devices.  

> **Note**  
> These examples should work on any MicroPython platform but need to absorb hardware difference.  
> All these examples runs as it is on MIMXRT1050-EVK. If you try on MIMXRT1170-EVK, the hardware I2C has different ID for A4/A5 pins. The ID must be changed from 0 to 2.  
> Refer to pinout document for each platforms. For i.MXRT, the pinout information is available [here](https://docs.micropython.org/en/latest/mimxrt/pinout.html#mimxrt-i2c-pinout).


?|File name|Folder|Description|Device type
---|---|---|---|---
💡|LED_controller.py						|example/general/|Simple sample: making an LED_controller instance and how PWM can be controlled										|PCA9955B, PCA9956B, PCA9957, PCA9632
💡|LED_gradation_ctrl.py					|example/general/|Gradation control (hardware) feature demo																						|PCA9955B, PCA9957
💡|LED_instance.py							|example/general/|Using another class to abstract LED controllers																	|PCA9955B, PCA9956B, PCA9957
💡|LED_demo.py								|example/general/|Showing idea to use ‘LED class’ to manage LED and white LED individually											|PCA9955B, PCA9956B, PCA9957, PCA9632
💡|LED_demo_dual_om13321.py					|example/general/|Showing idea to use ‘LED class’ to manage multiple LED controller devices											|PCA9956B
⏰|RTC_demo_PCF2131_ARD.py					|example/general/|Operate a PCF2131 through MicroPython’s machine.RTC equivalent APIs. Using 2 interrupt lines						|PCF2131
⏰|RTC_demo_PCF85063AT_ARD.py				|example/general/|Operate a PCF85063 through MicroPython’s machine.RTC equivalent APIs. 											|PCF85063
🌡️|temp_sensor_simple_PCT2075_LM75B.py							|example/general/	|Very simple sample to operate a temp sensor												|LM75B, PCT2075
🌡️|temp_sensor_simple_P3T1085_P3T1755_P3T1035_P3T2030.py		|example/general/	|Very simple sample to operate a temp sensor with different I2C pin assign. 				|P3T1085, P3T1755, P3T1035, P3T2030
🌡️|temp_sensor_simple_P3T1085_P3T1755_P3T1035_P3T2030-ARD.py	|example/ARD_boards/|Similar to “temp_sensor_simple.py” but different I2C pin assign. 							|P3T1085, P3T1755, P3T1035, P3T2030
🌡️|temp_sensor_demo_PCT2075DP-ARD.py		|example/ARD_boards/|Operate with interrupt and heater-resister on ARD board															|PCT2075
🌡️|temp_sensor_demo_P3T1085UK-ARD.py		|example/ARD_boards/|Similar to “temp_sensor_demo_PCT2075DP-ARD” but no heater operation												|P3T1085
🌡️|temp_sensor_demo_P3T1755DP-ARD.py		|example/ARD_boards/|Similar to “temp_sensor_demo_PCT2075DP-ARD” but no heater operation												|P3T1755
🌡️|temp_sensor_demo_P3T1035_P3T2030-ARD.py	|example/ARD_boards/|All 8 sensors operated together												|P3T1035, P3T2030
↕|GPIO_demo.py								|example/general/|Operation sample of a PCA9555 API																					|PCA9555
↕|GPIO_demo_PCAL6xxxA-ARD.py				|example/general/|Operation sample of a PCAL6xxx ARD board. Using interrupt															|PCAL6408, PCAL6416, PCAL6524, PCAL6534
🔠|LCD_demo_PCA8561AHN-ARD.py				|example/general/|Shows direct ON/OFF of segments and using  putc(), puts() methods													|PCA8561
💁|protocol_bridge_SC16IS7xx.py				|example/general/|Operate an I²C/SPI to UART protocol bridge through MicroPython’s machine.UART equivalent APIs. 					|SC16IS7xx
💁|protocol_bridge_SC18IS606_with_AT25010.py|example/general/|Operate an I²C to SPI protocol bridge through MicroPython’s machine.SPI equivalent APIs. AT25010 as an SPI target	|SC18IS606
🔄|stepper_motor_simple.py					|example/general/|Operating stepping motor with simple API																			|PCA9629A
🔄|stepper_motor_5_motors.py				|example/general/|Operating 5 instances of PCA9629A class																			|PCA9629A
🍎|accelerometer.py							|example/general/|Simple 3 axis data capturing from FXOS8700 or FXLS8974																|FXOS8700, FXLS8974
🍎|magnetometer.py							|example/general/|Simple compass application using FXOS8700																			|FXOS8700
🌊|afe.py									|example/general/|Simple AFE (NAFE13388) operation to show measured voltage on 2 input channels										|NAFE13388
## Demo (remote demo)
The demo code is avaiable in `remote_demo/`.  
`remote_demo/start_w_auto_IP(DHCP).py` and `remote_demo/start_w_fixed_IP.py` are start scripts to run the demo.  
This demonstration works with a network connection. The microcontroller performs a HTTP server to provide user interface on web browsers.  

For more information, refer to [`remote_demo/README.md`](https://github.com/teddokano/mikan/blob/main/remote_demo/README.md).

Video is available --> [https://youtu.be/usPzhs_2IsI](https://youtu.be/usPzhs_2IsI)   
[![](https://github.com/teddokano/additional_files/blob/main/mikan/img/remo_demo_perform.png)](https://youtu.be/usPzhs_2IsI)
 
How to setup? --> [https://youtu.be/fkHqdnd4t1s](https://youtu.be/fkHqdnd4t1s)  
[![](https://github.com/teddokano/additional_files/blob/main/mikan/img/remo_demo_install.png)](https://youtu.be/fkHqdnd4t1s)

# Applying modification
Refer to [How a new device can be added?](https://github.com/teddokano/mikan/blob/main/how_to_add_a_new_device.md)


💡⏰🌡️↕🔠🔄💁🍎🌊
