"""
LED controller operation library for MicroPython
Akifumi (Tedd) OKANO / Released under the MIT license

version	0.1 (29-Sep-2022)
"""
from nxp_periph.I2C_interface	import	I2C_target

class LED_controller_base:
	"""
	An abstraction class to make user interface.
	"""
	
	def pwm( self, *args ):
		"""
		PWM setting

		Takes 1 or 2 arguments.
		
		If 2 arguments are geven, it takes as register-name/address
		and PWM setting value.
		
		If only 1 argument is geven, it takes the agrgument as list.
		The list may need to contain the number of LED controller
		channels (self.CHANNELS) elements.

		Parameters (if 2 arguments given)
		----------
		args[0] : string or int
			Register name or pointer to the register.
		args[1] : int or float
			PWM ratio in range of 0~255 or 0.0~1.0
			
		Parameters (if 1 argument given)
		----------
		args[0] : list
			The list may need to contain the number of LED
			controller channels (self.CHANNELS) elements.
			Values are PWM ratio should be in range of
			0~255 or 0.0~1.0
			
		"""
		if 2 == len( args ):
			r	= self.__pwm_base + args[ 0 ]
			v	= args[ 1 ] if isinstance( args[ 1 ], int ) else int( args[ 1 ] * 255.0 )
			self.write_registers( r, v )
		elif 1 == len( args ):
			l	= [ v if isinstance( v, int ) else v * 255.0 for v in args[ 0 ] ]
			self.write_registers( self.__pwm_base, l )


class PCA995xB_base( LED_controller_base, I2C_target ):
	"""
	An abstraction class for PCA995x family
	"""
	DEFAULT_ADDR		= 0xE0 >> 1

	AUTO_INCREMENT		= 0x80
	PWM_INIT			= 0x00
	IREF_INIT			= 0x10

	def __init__( self, i2c, address = DEFAULT_ADDR, pwm = PWM_INIT, iref = IREF_INIT, current_control = False ):
		"""
		PCA995xB_base constructor
	
		Parameters
		----------
		i2c		: machine.I2C instance
		address	: I2C target (device) address
		pwm		: int, option
			Initial PWM value
		iref	: int, option
			Initial IREF (current setting) value
		current_control : bool, option
			Brightness control switch PWM or current.
			Default:PWM (False)

		"""
		super().__init__( i2c, address, auto_increment_flag = self.AUTO_INCREMENT )
		self.__pwm_base	= self.REG_NAME.index( "IREF0" if current_control else "PWM0" )
		
		init	=	{
						"LEDOUT0": [ 0xAA ] * (self.CHANNELS // 4),
						"PWMALL" : pwm,
						"IREFALL": iref
					}
					
		for r, v in init.items():	#	don't care: register access order
			self.write_registers( r, v )
	
		self.pwm_setting	= [ pwm ] * self.CHANNELS


class PCA9955B( PCA995xB_base ):
	CHANNELS		= 16
	REG_NAME		=	(
							"MODE1", "MODE2",
							"LEDOUT0", "LEDOUT1", "LEDOUT2", "LEDOUT3",
							"GRPPWM", "GRPFREQ",
							"PWM0",  "PWM1", "PWM2",  "PWM3",  "PWM4",  "PWM5",  "PWM6",  "PWM7",
							"PWM8",  "PWM9", "PWM10", "PWM11", "PWM12", "PWM13", "PWM14", "PWM15",
							"IREF0", "IREF1", "IREF2",  "IREF3",  "IREF4",  "IREF5",  "IREF6",  "IREF7",
							"IREF8", "IREF9", "IREF10", "IREF11", "IREF12", "IREF13", "IREF14", "IREF15",
							"RAMP_RATE_GRP0", "STEP_TIME_GRP0", "HOLD_CNTL_GRP0", "IREF_GRP0",
							"RAMP_RATE_GRP1", "STEP_TIME_GRP1", "HOLD_CNTL_GRP1", "IREF_GRP1",
							"RAMP_RATE_GRP2", "STEP_TIME_GRP2", "HOLD_CNTL_GRP2", "IREF_GRP2",
							"RAMP_RATE_GRP3", "STEP_TIME_GRP3", "HOLD_CNTL_GRP3", "IREF_GRP3",
							"GRAD_MODE_SEL0", "GRAD_MODE_SEL1",
							"GRAD_GRP_SEL0", "GRAD_GRP_SEL1", "GRAD_GRP_SEL2", "GRAD_GRP_SEL3",
							"GRAD_CNTL",
							"OFFSET",
							"SUBADR1", "SUBADR2", "SUBADR3", "ALLCALLADR",
							"PWMALL", "IREFALL",
							"EFLAG0", "EFLAG1", "EFLAG2", "EFLAG3"
						)


class PCA9956B( PCA995xB_base ):
	CHANNELS		= 24
	REG_NAME		=	(
							"MODE1", "MODE2",
							"LEDOUT0", "LEDOUT1", "LEDOUT2", "LEDOUT3", "LEDOUT4", "LEDOUT5",
							"GRPPWM", "GRPFREQ",
							"PWM0",  "PWM1",  "PWM2",  "PWM3",  "PWM4",  "PWM5",
							"PWM6",  "PWM7",  "PWM8",  "PWM9",  "PWM10", "PWM11",
							"PWM12", "PWM13", "PWM14", "PWM15", "PWM16", "PWM17",
							"PWM18", "PWM19", "PWM20", "PWM21", "PWM22", "PWM23",
							"IREF0",  "IREF1",  "IREF2",  "IREF3",  "IREF4",  "IREF5",
							"IREF6",  "IREF7",  "IREF8",  "IREF9",  "IREF10", "IREF11",
							"IREF12", "IREF13", "IREF14", "IREF15", "IREF16", "IREF17",
							"IREF18", "IREF19", "IREF20", "IREF21", "IREF22", "IREF23",
							"OFFSET",
							"SUBADR1", "SUBADR2", "SUBADR3", "ALLCALLADR",
							"PWMALL", "IREFALL",
							"EFLAG0", "EFLAG1", "EFLAG2", "EFLAG3", "EFLAG4", "EFLAG5"
						)

