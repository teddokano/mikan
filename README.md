# mp_driver
Peripheral device driver collection for MicroPython

## What is this?
NXP peripheral device drivers and sample/demo codes. 
The drivers provided to operate I2C/SPI peripheral devices easy. 

## Getting started

### Video
YouTube video available for guiding easy install and demo ;)

[![](https://img.youtube.com/vi/miob6jZ-87g/0.jpg)](https://www.youtube.com/watch?v=miob6jZ-87g)

### Steps
1. Check sys.path on target board
	1. Connect your MCU board and PC, get REPL environment
	1. Chack path setting by typing.. 
	```
	>>> import sys
	>>> print(sys.path)
	```
	Then you will get list of path like (in case of MIMXRT1050_EVK)
	```
	['', '.frozen', '/flash', '/flash/lib']
	```
	or  (in case of Raspberry Pi Pico)
	```
	['', '.frozen', '/lib']
	```
1. Copy "nxp_periph" into target's' "lib" (it could be '/flash/lib' or '/lib') nameed folder. 
1. Now it's ready to play! Choose an example code in "example" folder and run.

## Supported devices
- Real Time Clock (RTC)
	- PCF2131 (I2C / SPI)
	- PCF85063
- Temperature sensor
	- LM75B
	- PCT2075
- LED controller
	- PCA9632 (PCA9633 compatible)
	- PCA9955B
	- PCA9956B
	- PCA9957
- GPIO expander
	- PCA9555 (PCA9555A, PCA9539 compatible)
	- PCA9554 (PCA9554A, PCA9554B, PCA9554C, PCA9538 compatible)
- Stepper motor controller
	- PCA9629A
