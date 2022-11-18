from	nxp_periph.interface	import	I2C_target
from	utime					import	sleep

class StepperMotor_base():
	"""
	An abstraction class to make user interface.
	"""

	def start( self, reverse = False ):
		self.__start( start = True, reverse = reverse )

	def stop( self ):
		self.__start( start = False )

	def steps( self, step, reverse = False ):
		self.__steps( step, reverse = reverse )

	def pps( self, pps, reverse = False ):
		self.__pps( pps, reverse = reverse )

	def drv_phase( self, v ):
		self.__drv_phase( v )

	def home( self, pps = 96, reverse = False, extrasteps = 0 ):
		self.__home( pps = pps, reverse = reverse, extrasteps = extrasteps )
	
	def init():
		__init_reg()

	def w16( self, reg, val ):
		self.write_registers( reg, [ val & 0xFF, val >> 8 ] )

	def r16( self, reg ):
		r	= self.read_registers( reg, 2 )
		return r[ 0 ] | ( r[ 1 ] << 8 )

class PCA9629A( StepperMotor_base, I2C_target ):
	STEP_RESOLUTION	= 1/(3e-6)
	DEFAULT_ADDR	= 0x40 >> 1
	AUTO_INCREMENT	= 0x80

	REG_NAME	= ( "MODE",
					"WDTOI", "WDCNTL",
					"IO_CFG",
					"INTMODE", "MSK", "INTSTAT",
					"IP",
					"INT_MTR_ACT", "EXTRASTEPS0", "EXTRASTEPS1",
					"OP_CFG_PHS", "OP_STAT_TO",
					"RUCNTL",
					"RDCTNL",
					"PMA",
					"LOOPDLY_CW", "LOOPDLY_CCW",
					"CWSCOUNTL", "CWSCOUNTH", "CCWSCOUNTL", "CCWSCOUNTH",
					"CWPWL", "CWPWH", "CCWPWL", "CCWPWH",
					"MCNTL",
					"SUBADR1", "SUBADR2", "SUBADR3", "ALLCALLADR",
					"STEPCOUNT0", "STEPCOUNT1", "STEPCOUNT2", "STEPCOUNT3",
					)

	def __init__( self, i2c, address = DEFAULT_ADDR, steps_per_rotation = 48 ):
		I2C_target.__init__( self, i2c, address, auto_increment_flag = self.AUTO_INCREMENT )
		self.steps_per_rotation	= steps_per_rotation

	def __init_reg( self ):
		data	= [
					 0x20, 0x0A, 0x00, 0x03, 0x13, 0x1C,             #	for registers MODE - MSK (0x00 - 0x07)
					 0x00, 0x00, 0x68, 0x00, 0x00,                   #	for registers INTSTAT - EXTRASTEPS1 (0x06, 0xA)
					 0x10, 0x80,                                     #	for registers OP_CFG_PHS and OP_STAT_TO (0x0B - 0xC)
					 0x09, 0x09, 0x01, 0x7D, 0x7D,                   #	for registers RUCNTL - LOOPDLY_CCW (0xD- 0x10)
					 0xFF, 0x01, 0xFF, 0x01, 0x05, 0x0D, 0x05, 0x0D, #	for registers CWSCOUNTL - MCNTL (0x12 - 0x1A)
					 0x20,                                           #	for register MCNTL (0x1A)
					 0xE2, 0xE4, 0xE6, 0xE0                          #	for registers SUBADR1 - ALLCALLADR (0x1B - 0x1E)
					]
		self.write_registers( "MODE", data )
	
	def __start( self, start = True, reverse = False ):
		if start:
			self.write_registers( "MCNTL", 0xC0 | (1 if reverse else 0) )
		else:
			self.write_registers( "MCNTL", 0xA0 )

	def __pps( self, pps, reverse = False ):
		prescaler		= 0
		ratio	= int( 40.6901 / pps )
		
		for i in range( 1, 8 ):
			prescaler	= i if ratio & (0x1 << i) else prescaler
		
		pulse_width	 = int( self.STEP_RESOLUTION / ((0x1 << prescaler) * pps) )
		#print( "prescaler = {}, pulse_width = {}".format( prescaler, pulse_width ) )
		pulse_width	|= prescaler << 13
		
		self.w16( "CCWPWL" if reverse else "CWPWL", pulse_width )
		
		return pulse_width

	def __drv_phase( self, v ):
		v	= int( 0x3 if v == 0.5 else (v - 1)  )		
		self.bit_operation( "OP_CFG_PHS", 0xC0, v << 6 )

	def __steps( self, step, reverse = False ):
		self.w16( "CCWSCOUNTL" if reverse else "CWSCOUNTL", step )

	def __home( self, pps = 96, reverse = False, extrasteps = 0 ):
		data	= [ 0x03, 0x13, 0x1C, 0x00, 0x00, 0x01, extrasteps, 0x00 ]  #  for registers IO_CFG - EXTRASTEPS1 (0x03 - 0x0A)
		self.write_registers( "IO_CFG", data )
		self.pps( pps, reverse = reverse )
		self.start( reverse = reverse )
