# "mikan" 💡⏰🌡️↕🔄
Peripheral device driver for collection for MicroPython.  
_The name of this repository has been changed from "mp_driver" to "mikan" (2022 Nov 02)._


## What is this?
NXP peripheral device drivers (SDK) for [MicroPython](https://micropython.org) and its usage examples and demo.  
The drivers provided to operate I²C/SPI peripheral devices. It enables quick evaluation and rapid demo development by simple intuitive interface (API) and flexible MicroPython environment.  
Refer to this [video](https://youtu.be/vFyovJFih5Y) to find what can be done.

![Boards](https://github.com/teddokano/additional_files/blob/main/mikan/img/boards.jpeg)  
_[Arduino® Shields Solutions](https://www.nxp.com/design/development-boards/analog-toolbox/arduino-shields-solutions:ARDUINO-SOLUTIONS) boards and I²C peripheral evaluation boards with 
[i.MX RT1050 Evaluation Kit](https://www.nxp.com/design/development-boards/i-mx-evaluation-and-development-boards/i-mx-rt1050-evaluation-kit:MIMXRT1050-EVK)_  
  
![example_operation](https://github.com/teddokano/additional_files/blob/main/mikan/img/example_operation.png)  
_Screen shot of ~~`examples/temp_sensor_interrupt.py`~~ [`examples/temp_sensor_demo_PCT2075DP_ARB.py`](https://github.com/teddokano/mikan/blob/main/examples/temp_sensor_demo_PCT2075DP_ARB.py) operation_
  
![remote_demo](https://github.com/teddokano/additional_files/blob/main/mikan/img/remote_demo.png)
_"[remote_demo](https://github.com/teddokano/mikan/tree/main/remote_demo)" running. Device operation can be done from web browser_
  
## Supported devices
- Real Time Clock (RTC)
	- [PCF2131](https://www.nxp.com/products/peripherals-and-logic/signal-chain/real-time-clocks/rtcs-with-temperature-compensation/nano-power-highly-accurate-rtc-with-integrated-quartz-crystal:PCF2131) (for both I²C and SPI interface can be used)
	- [PCF85063A](https://www.nxp.com/products/peripherals-and-logic/signal-chain/real-time-clocks/rtcs-with-ic-bus/tiny-real-time-clock-calendar-with-alarm-function-and-ic-bus:PCF85063A)
- Temperature sensor
	- [LM75B](https://www.nxp.com/products/sensors/ic-digital-temperature-sensors/digital-temperature-sensor-and-thermal-watchdog:LM75B)
	- [PCT2075](https://www.nxp.com/products/sensors/ic-digital-temperature-sensors/ic-bus-fm-plus-1-degree-c-accuracy-digital-temperature-sensor-and-thermal-watchdog:PCT2075)
- LED controller
	- [PCA9632](https://www.nxp.com/products/power-management/lighting-driver-and-controller-ics/led-controllers/4-bit-fm-plus-ic-bus-low-power-led-driver:PCA9632) (PCA9633 compatible)
	- [PCA9955B](https://www.nxp.com/products/power-management/lighting-driver-and-controller-ics/led-drivers/16-channel-fm-plus-ic-bus-57-ma-20-v-constant-current-led-driver:PCA9955BTW)
	- [PCA9956B](https://www.nxp.com/products/power-management/lighting-driver-and-controller-ics/led-drivers/24-channel-fm-plus-ic-bus-57-ma-20-v-constant-current-led-driver:PCA9956BTW)
	- [PCA9957](https://www.nxp.com/products/power-management/lighting-driver-and-controller-ics/led-drivers/24-channel-spi-serial-bus-32-ma-5-5-v-constant-current-led-driver:PCA9957)
- GPIO expander
	- [PCA9555](https://www.nxp.com/products/interfaces/ic-spi-i3c-interface-devices/general-purpose-i-o-gpio/16-bit-ic-bus-and-smbus-i-o-port-with-interrupt:PCA9555) (PCA9555A, PCA9539 compatible)
	- [PCA9554](https://www.nxp.com/products/interfaces/ic-spi-i3c-interface-devices/general-purpose-i-o-gpio/8-bit-ic-bus-and-smbus-i-o-port-with-interrupt:PCA9554_PCA9554A) (PCA9554A, PCA9554B, PCA9554C, PCA9538 compatible)
- Stepper motor controller
	- [PCA9629A](https://www.nxp.com/products/interfaces/ic-spi-i3c-interface-devices/ic-bus-controller-and-bridge-ics/fm-plus-ic-bus-advanced-stepper-motor-controller:PCA9629APW)

## Getting started

### Video
YouTube video available for guiding easy install and examples 🙂  
[https://youtu.be/miob6jZ-87g](https://youtu.be/miob6jZ-87g)  
[![](https://github.com/teddokano/additional_files/blob/main/mikan/img/demodriver.png)](https://youtu.be/miob6jZ-87g)


### Steps
1. Check sys.path on target board
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
1. Copy "nxp_periph" folder into target's' "lib" (it could be '/flash/lib' or '/lib') named folder.  For file/folder copying, some tools can be used like [Thonny](https://thonny.org), [rshell](https://github.com/dhylands/rshell), etc.
1. Now it's ready to play! Choose an example code in "example" folder and run.

## What is inside?
### Drivers
The drivers are main part of this repo.  
The driver code files are in `nxp_periph/`.  
The drivers are provided as class-libraries with device names (type-numbers). With this class-libraries, the device operations are highly abstracted and simplified. Methods of the class-drivers enables major features of devices and and provides register level access for user custom operation. 

For example, for the LED controller (PCA9955B) ...
```python
from machine    import I2C      # Importing 'I²C' class library from MocroPython's 'machine' module
from utime      import sleep    # Importing 'sleep' from MocroPython's 'utime' module
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
from machine    import I2C     # Importing 'I²C' class library from MocroPython's 'machine' module
from utime      import sleep   # Importing 'sleep' from MocroPython's 'utime' module
from nxp_periph import PCT2075 # Importing the device class library of 'PCT2075'

i2c         = I2C( 0, freq = (400 * 1000) ) # Making an instance of I²C with 400kHz clock setting
temp_sensor = PCT2075( i2c )                # Making an instance of PCT2075 which is connected to the 'i2c'.

while True:                    # Looping following part forever
    value   = temp_sensor.temp # Reading temperature in celsius value
    print( value )             # Showing the value
    sleep( 1 )                 # Waiting for 1 second
```

For more information of examples, please find next section of this document. 

### Examples
The example code files are in `examples/` folder.  
It shows simple usage examples for the drivers and standalome demo for target devices.  

?|File name|Description|Device type
---|---|---|---
💡|LED_controller.py			| Most simple LED controller operation	| PCA9632, PCA9955B, PCA9956B, PCA9957
💡|LED_instance.py				| Sample for LED class library to abstract LEDs from LED controller devices | Any LED controllers
💡|LED_demo.py  				| Demo code for LED class library to gether LED by colors | Any LED controllers
💡|LED_demo_dual_om13321.py	| Demo code to operate multiple LED controllers | PCA9956B (for OM13321 evaluation boards)
💡|LED_gradation_ctrl.py		| Sample to operate gradation control feature | PCA9955B, PCA9957
⏰|RTC_demo_PCF2131_ARD.py		| RTC PCF2131 operation | PCF2131 (PCF2131-ARD board)
⏰|RTC_demo_PCF85063AT_ARD.py	| RTC PCF85063A operation | PCF85063A (PCF85063AT-ARD board)
🌡️|temp_sensor_simple.py		| Simple temperature sensor operation | LM75B, PCT2075 (LM75B compatible devices)
🌡️|temp_sensor_interrupt.py		| Demo for PCT2075DP-ARD operation | PCT2075 (PCT2075DP-ARD board)
↕|GPIO_demo.py               	| Simple operation for PCA9555	| PCA9555 (PCA9555 compatible devices)
🔄|stepper_motor_simple.py		| Simple operation for PCA9629A	| PCA9629A

### Demo (remote demo)
The demo code is avaiable in `remote_demo/`.  
`remote_demo/DEMO.py` has 'main()' function to start the demo.  
This demonstration works with a network connection. The microcontroller performs a HTTP server to provide user interface on web browsers.  
Video is available --> [https://youtu.be/usPzhs_2IsI](https://youtu.be/usPzhs_2IsI)   
[![](https://github.com/teddokano/additional_files/blob/main/mikan/img/remo_demo_perform.png)](https://youtu.be/usPzhs_2IsI)
 

How to setup? --> [https://youtu.be/fkHqdnd4t1s](https://youtu.be/fkHqdnd4t1s)  
[![](https://github.com/teddokano/additional_files/blob/main/mikan/img/remo_demo_install.png)](https://youtu.be/fkHqdnd4t1s)



💡⏰🌡️↕🔄
