# How to add a new device
mikan is a collection of I²C・SPI peripheral devices.  
This document a step by step guide to add a new device. 

# Step 0 : 


# Step 1 : Prepare a file
A skelton code (\_skelton.py) is available in `nxp_periph/` folder.  
Copy and rename the file. Name can be a device type number or device category.  

In this guide, I'll try to add a FXOS8700.  
So I copied `nxp_periph/_skelton.py` and renamed as `nxp_periph/FXOS8700.py` 

# Step 2 : Check the environment
Open the `nxp_periph/FXOS8700.py` file.  
This file is a tiny micropython application code which can run by itself.  
It's a minimum code to work with mikan's class libraries.  

```python
from nxp_periph.interface	import	I2C_target
from machine				import	I2C

def main():
	i2c			= I2C( 0, freq = (400 * 1000) )
	myInstance	= myClass( i2c )

	print( i2c.scan() )
	print( myInstance.do_something() )

class myClass( I2C_target ):
	DEFAULT_ADDR	= 0xAA
	REG_NAME		= ()

	def __init__( self, i2c, address = DEFAULT_ADDR ):
		super().__init__( i2c, address )
		
	def do_something( self ):
		return "hello " + self.__class__.__name__
		
if __name__ == "__main__":
	main()
```

Execute the code to check mikan is installed properly. 
It will show following message on shell screen.  
A list in first line is a I²C scan result. It will be an empty list if no device is connected.  
In this sample, 2 I²C devices are found. The address 31 (0x1F) device is an FXOS8700.  
```
>>> %Run -c $EDITOR_CONTENT
[26, 31]
hello myClass
>>> 
```

# Step 3 : Start to overwriting the code
Start to overwriting the code for FXOS8700.  
First, change 4 part of code needed to be modified.  
In this sample, the overwritten lines are shown with `###` in the line head to show what part was modified.  

```python
from nxp_periph.interface	import	I2C_target
from machine				import	I2C

def main():
	i2c			= I2C( 0, freq = (400 * 1000) )
### myInstance	= myClass( i2c )
	acc		= FXOS8700( i2c )

	print( i2c.scan() )
### print( myInstance.do_something() )
	print( acc.do_something() )

###class myClass( I2C_target ):
class FXOS8700( I2C_target ):
### DEFAULT_ADDR	= 0xAA
	DEFAULT_ADDR	= 0x1F
	REG_NAME		= ()

	def __init__( self, i2c, address = DEFAULT_ADDR ):
		super().__init__( i2c, address )
		
	def do_something( self ):
		return "hello " + self.__class__.__name__
		
if __name__ == "__main__":
	main()
```

Of course those `###` lines are not necessary. You can erase those in actual code.  
Following sample shows the code after removing `###` lines. 

```python
from nxp_periph.interface	import	I2C_target
from machine				import	I2C

def main():
	i2c		= I2C( 0, freq = (400 * 1000) )
	acc		= FXOS8700( i2c ) #	<-- Changed to make a new instance with new class

	print( i2c.scan() )
	print( acc.do_something() ) #	<-- Changed to work with a new instance

class FXOS8700( I2C_target ): #	<-- Changed to define a new class name
	DEFAULT_ADDR	= 0x1F #	<-- Changed to give a default I²C address
	REG_NAME		= ()

	def __init__( self, i2c, address = DEFAULT_ADDR ):
		super().__init__( i2c, address )
		
	def do_something( self ):
		return "hello " + self.__class__.__name__
		
if __name__ == "__main__":
	main()
```

Execute the code and confirm the class name has been changed. 

```
>>> %Run -c $EDITOR_CONTENT
[26, 31]
hello FXOS8700
>>> 
```

# Step 4 : Adding register list
For ease of class library operation, mikan provides register operation interface which can accesed by register name.  
A class variable `REG_NAME` enables to make this interface.  
Copy register names from datasheet and paste those as strings in a tupple.  

> **Note**
The register name list need to be in sequential. If there is some unused register address, those are needed to be filled with a dummy name like "Reserved". 

```python
from nxp_periph.interface	import	I2C_target
from machine				import	I2C

def main():
	i2c		= I2C( 0, freq = (400 * 1000) )
	acc		= FXOS8700( i2c )

	print( i2c.scan() )
	print( acc.do_something() )

class FXOS8700( I2C_target ):
	DEFAULT_ADDR	= 0x1F
	REG_NAME	= ( "STATUS", 
					"OUT_X_MSB", "OUT_X_LSB", "OUT_Y_MSB", "OUT_Y_LSB", "OUT_Z_MSB", "OUT_Z_LSB", 
					"Reserved", "Reserved", 
					"F_SETUP", "TRIG_CFG", "SYSMOD", "INT_SOURCE", "WHO_AM_I", "XYZ_DATA_CFG", "HP_FILTER_CUTOFF", 
					"PL_STATUS", "PL_CFG", "PL_COUNT", "PL_BF_ZCOMP", "PL_THS_REG", 
					"A_FFMT_CFG", "A_FFMT_SRC", "A_FFMT_THS", "A_FFMT_COUNT", 
					"Reserved", "Reserved", "Reserved", "Reserved", 
					"TRANSIENT_CFG", "TRANSIENT_SRC", "TRANSIENT_THS", "TRANSIENT_COUNT", 
					"PULSE_CFG", "PULSE_SRC", "PULSE_THSX", "PULSE_THSY", "PULSE_THSZ", "PULSE_TMLT", "PULSE_LTCY", "PULSE_WIND", 
					"ASLP_COUNT", 
					"CTRL_REG1", "CTRL_REG2", "CTRL_REG3", "CTRL_REG4", "CTRL_REG5", 
					"OFF_X", "OFF_Y", "OFF_Z", 
					"M_DR_STATUS", 
					"M_OUT_X_MSB", "M_OUT_X_LSB", "M_OUT_Y_MSB", "M_OUT_Y_LSB", "M_OUT_Z_MSB", "M_OUT_Z_LSB", 
					"CMP_X_MSB", "CMP_X_LSB", "CMP_Y_MSB", "CMP_Y_LSB", "CMP_Z_MSB", "CMP_Z_LSB", 
					"M_OFF_X_MSB", "M_OFF_X_LSB", "M_OFF_Y_MSB", "M_OFF_Y_LSB", "M_OFF_Z_MSB", "M_OFF_Z_LSB", 
					"MAX_X_MSB", "MAX_X_LSB", "MAX_Y_MSB", "MAX_Y_LSB", "MAX_Z_MSB", "MAX_Z_LSB", "MIN_X_MSB", "MIN_X_LSB", "MIN_Y_MSB", "MIN_Y_LSB", "MIN_Z_MSB", "MIN_Z_LSB", 
					"TEMP", 
					"M_THS_CFG", "M_THS_SRC", 
					"M_THS_X_MSB", "M_THS_X_LSB", "M_THS_Y_MSB", "M_THS_Y_LSB", "M_THS_Z_MSB", "M_THS_Z_LSB", "M_THS_COUNT", 
					"M_CTRL_REG1", "M_CTRL_REG2", "M_CTRL_REG3", "M_INT_SRC", 
					"A_VECM_CFG", "A_VECM_THS_MSB", "A_VECM_THS_LSB", 
					"A_VECM_CNT", "A_VECM_INITX_MSB", "A_VECM_INITX_LSB", "A_VECM_INITY_MSB", "A_VECM_INITY_LSB", "A_VECM_INITZ_MSB", "A_VECM_INITZ_LSB", 
					"M_VECM_CFG", "M_VECM_THS_MSB", "M_VECM_THS_LSB", 
					"M_VECM_CNT", "M_VECM_INITX_MSB", "M_VECM_INITX_LSB", "M_VECM_INITY_MSB", "M_VECM_INITY_LSB", "M_VECM_INITZ_MSB", "M_VECM_INITZ_LSB", "A_FFMT_THS_X_MSB", "A_FFMT_THS_X_LSB", "A_FFMT_THS_Y_MSB", "A_FFMT_THS_Y_LSB", "A_FFMT_THS_Z_MSB", "A_FFMT_THS_Z_LSB", 
					"Reserved"
					)

	def __init__( self, i2c, address = DEFAULT_ADDR ):
		super().__init__( i2c, address )
		
	def do_something( self ):
		return "hello " + self.__class__.__name__
		
if __name__ == "__main__":
	main()
```

# Step 5 : Check register operation
Add `dump_reg()` method call in the main function and run.  

```python
def main():
	i2c		= I2C( 0, freq = (400 * 1000) )
	acc		= FXOS8700( i2c )

	print( i2c.scan() )
	print( acc.do_something() )
	acc.dump_reg() # <-- Added

class FXOS8700( I2C_target ):
	DEFAULT_ADDR	= 0x1F
	REG_NAME	= ( "STATUS", 
	...
	..
```

Check the result of execution and confirm the register names are shown with proper register address. 

```
>>> %Run -c $EDITOR_CONTENT
[26, 31]
hello FXOS8700
register dump: "FXOS8700", target address 0x1F (0x3E)
    STATUS           (0x00) : 0x00    CMP_Z_MSB        (0x3D) : 0x56
    OUT_X_MSB        (0x01) : 0x13    CMP_Z_LSB        (0x3E) : 0x20
    OUT_X_LSB        (0x02) : 0xB8    M_OFF_X_MSB      (0x3F) : 0x00
    OUT_Y_MSB        (0x03) : 0xC1    M_OFF_X_LSB      (0x40) : 0x13
    OUT_Y_LSB        (0x04) : 0xF4    M_OFF_Y_MSB      (0x41) : 0xB8
    OUT_Z_MSB        (0x05) : 0x56    M_OFF_Y_LSB      (0x42) : 0xC1
    OUT_Z_LSB        (0x06) : 0x20    M_OFF_Z_MSB      (0x43) : 0xF4
	...
	..
    CMP_Y_MSB        (0x3B) : 0xC1    A_FFMT_THS_Z_LSB (0x78) : 0x13
    CMP_Y_LSB        (0x3C) : 0xF4    Reserved         (0x79) : 0xB8
>>> 
```

> **Warning**
In case of FXOS8700, it has unique modes of auto-increment register access. 
To avoid effect of auto-increment, each single register access is required for register dump.  
It can be done by defining a method of `dump` in FXOS8700 class which over-rides same name method in super class. 
```python
	def dump( self ):
		rtn	= []
		for r in self.REG_NAME:
			rtn	+= [ self.read_registers( r, 1 ) ]
		
		return rtn
```


# Step 6 : Add required device initialization
The device may need some initialization to start operation.  
These operation may not be needed if you let users do it by themselves.  
However, it may be good idea to provide initializations when the instance is made. It can simplify user code.  

Add the device initial settings in `__init__()` method. 

```python
class FXOS8700( I2C_target ):
	...
	..
	def __init__( self, i2c, address = DEFAULT_ADDR ):
		super().__init__( i2c, address )
		
		self.write_registers( "F_SETUP", 0x00 )     # <-- added
		self.write_registers( "CTRL_REG1", 0x01 )   # <-- added
		self.write_registers( "M_CTRL_REG1", 0x03 ) # <-- added
```

# Step 7 : Add device operation method
Add device operation method to set/get device data.  
Next sample shows how the 
```python
from nxp_periph.interface	import	I2C_target
from machine				import	I2C
from utime					import	sleep	# <-- added

def main():
	i2c		= I2C( 0, freq = (400 * 1000) )
	acc		= FXOS8700( i2c )

	print( i2c.scan() )
	print( acc.do_something() )
	acc.dump_reg()

	while True:            # <-- added
		print( acc.xyz() ) # <-- added
		sleep( 0.5 )       # <-- added
		

class FXOS8700( I2C_target ):
	DEFAULT_ADDR	= 0x1F
	REG_NAME	= ( "STATUS", 
	...
	..
	
	def __init__( self, i2c, address = DEFAULT_ADDR ):
		super().__init__( i2c, address )
		
		self.write_registers( "F_SETUP", 0x00 )
		self.write_registers( "CTRL_REG1", 0x01 )
		self.write_registers( "M_CTRL_REG1", 0x03 )

	def xyz( self ):                                 # <-- added
		return self.read_registers( "OUT_X_MSB", 6 ) # <-- added
	
	def do_something( self ):
		return "hello " + self.__class__.__name__
		
if __name__ == "__main__":
	main()
```
The code will show result of periodic register read. 

```
>>> %Run -c $EDITOR_CONTENT
[26, 31]
hello FXOS8700
register dump: "FXOS8700", target address 0x1F (0x3E)
    STATUS           (0x00) : 0xFF    CMP_Z_MSB        (0x3D) : 0x3F
    OUT_X_MSB        (0x01) : 0xFE    CMP_Z_LSB        (0x3E) : 0xE0
    ...
    ..
    CMP_Y_LSB        (0x3C) : 0x20    Reserved         (0x79) : 0x58
[254, 176, 0, 80, 63, 80]
[254, 104, 0, 48, 63, 96]
[254, 176, 0, 40, 63, 112]
[254, 128, 0, 40, 63, 64]
[254, 216, 255, 248, 62, 232]

```

# Step 8 : Organizing data
Organize the data to present in user friendly format.  
In this sample, the data is retrieved as bytearray and converted to 16bit signed-int data using `ustruct.unpack`

```python
from nxp_periph.interface	import	I2C_target
from machine				import	I2C
from utime					import	sleep
from ustruct 				import	unpack	# <-- added

def main():
	...
	..
class FXOS8700( I2C_target ):
	...
	..
	def xyz( self ):	# <-- this method has been modified
		r	= self.read_registers( "OUT_X_MSB", 6, barray = True )
		r	= unpack( ">hhh", r )
		return r
```

```
>>> %Run -c $EDITOR_CONTENT
[26, 31]
hello FXOS8700
register dump: "FXOS8700", target address 0x1F (0x3E)
    STATUS           (0x00) : 0xFF    CMP_Z_MSB        (0x3D) : 0x3F
    OUT_X_MSB        (0x01) : 0xFE    CMP_Z_LSB        (0x3E) : 0x40
    ...
    ..
    CMP_Y_LSB        (0x3C) : 0x00    Reserved         (0x79) : 0xD0
(-408, 24, 16240)
(-336, 40, 16312)
(-376, 8, 16296)
(-368, 160, 16280)
(-352, 8, 16264)
(-360, -8, 16208)
(-280, 8, 16256)
```

# Step 9 : Organizing data 2
Further better data reprezentation, data may be organized in a defined unit.  
In this case, the accelerometer full-scale range is operated in +/-2 g. 
```python
	...
	..
	def xyz( self ):	# <-- this method has been modified
		r	= self.read_registers( "OUT_X_MSB", 6, barray = True )
		r	= unpack( ">hhh", r )
		r	= [ d / 2**15 * 2 for d in r ]
		return r
	...
	..
```


```
>>> %Run -c $EDITOR_CONTENT
[26, 31]
hello FXOS8700
register dump: "FXOS8700", target address 0x1F (0x3E)
    STATUS           (0x00) : 0xFF    CMP_Z_MSB        (0x3D) : 0x3F
    OUT_X_MSB        (0x01) : 0xFE    CMP_Z_LSB        (0x3E) : 0x40
    ...
    ..
    CMP_Y_LSB        (0x3C) : 0x00    Reserved         (0x79) : 0xD0
[-0.02294921875, 0.0029296875, 0.99365234375]
[-0.0234375, 0.0029296875, 0.990234375]
[-0.025390625, -0.0029296875, 0.990234375]
[-0.017578125, -0.001953125, 0.99072265625]
[-0.021484375, -0.00146484375, 0.986328125]
[-0.0205078125, 0.00244140625, 0.98828125]
[-0.0185546875, -0.0009765625, 0.9892578125]
[-0.01904296875, 0.00048828125, 0.99462890625]
```
