from nxp_periph.interface	import	I2C_target
from ustruct 				import	unpack

class ACCELEROMETER_base:
	"""
	An abstraction class to make user interface.
	"""
	def three_axis( self, reg ):
		"""
		get 3-axis data
		
		Parameters
		----------
		reg : int or string
			1st register pointer or name
			
		Returns
		-------
		int, int, int : 3 integers as 16bit register values

		"""
		
		return self.__three_axis( reg )

	def xyz( self ):
		"""
		get 3-axis "g" (gravitational acceleration) data
		
		Parameters
		Returns
		-------
		float, float, float : 3 "g" values

		"""

		return self.__xyz()

	def fullscale( self, g ):
		"""
		Fullscale setting

		Parameters
		----------
		g		: settting value

		"""
		self.__fullscale( g )

	def dump( self ):
		"""
		Overriding "dump()" in nxp_periph.interface class
		"""
		rtn	= []
		for r in self.REG_NAME:
			rtn	+= [ self.read_registers( r, 1 ) ]
		
		return rtn

class FXOS8700( ACCELEROMETER_base,I2C_target ):
	"""
	FXOS8700: 6-axis accerelometer and magnetometer
	
	A device class for a 6-axis accerelometer and magnetometer
	This class enables to get its realtime data 
	
	"""
	DEFAULT_ADDR		= 0x1F

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
		"""
		Initializer for FXOS8700 class instance

		Parameters
		----------
		i2c		: I2C instance
		address	: int, option

		"""
		super().__init__( i2c, address )
		
		self.write_registers( "F_SETUP",     0x00 )	# FIFO is disabled
		self.write_registers( "CTRL_REG1",   0x01 )	# active
		self.write_registers( "M_CTRL_REG1", 0x03 )	# hybrid mode, both accelerometer and magnetometer sensors are active
		self.write_registers( "M_CTRL_REG2", 0x20 )	# can be read xyz and mag together in 12 bytes

		self.fs_range	= 2
		self.fullscale( self.fs_range )

	def __three_axis( self, reg ):
		return unpack( ">hhh", self.read_registers( reg, 6, barray = True ) )
	
	def __xyz( self ):
		return [ d / 2**15 * self.fs_range for d in self.three_axis( "OUT_X_MSB" ) ]	# convert to G

	def __fullscale( self, v ):
		if 8 <= v:
			setting	= 0x2
		elif 4 <= v:
			setting	= 0x1
		else:
			setting	= 0x0
		
		self.bit_operation( "XYZ_DATA_CFG", 0x03, setting )

	def mag( self ):
		"""
		get 3-axis magnetometer output in nano-Tesla
		
		Parameters
		Returns
		-------
		int, int, int : 3-axis magnetometer output values

		"""
		return [ d * 100 for d in self.three_axis( "M_OUT_X_MSB" ) ]	# convert to nano-T

	def six_axis( self ):
		"""
		get 6-axis accelerometer and magnetometer outputs
		
		Parameters
		Returns
		-------
		int, int, int : 3-axis accelerometer 3-axis magnetometer outputs as 16bit register values

		"""
		return unpack( ">hhhhhh", self.read_registers( "OUT_X_MSB", 12, barray = True ) )

class FXLS8974( ACCELEROMETER_base, I2C_target ):
	"""
	FXLS8974: 3-axis accerelometer
	
	A device class for a 3-axis accerelometer
	This class enables to get its realtime data 
	
	"""
	DEFAULT_ADDR		= 0x19

	REG_NAME	= ( "INT_STATUS", "TEMP_OUT", "VECM_LSB", "VECM_MSB",
					"OUT_X_LSB", "OUT_X_MSB",
					"OUT_Y_LSB", "OUT_Y_MSB",
					"OUT_Z_LSB", "OUT_Z_MSB",
					"RESERVED_REG1",
					"BUF_STATUS",
					"BUF_X_LSB", "BUF_X_MSB",
					"BUF_Y_LSB", "BUF_Y_MSB",
					"BUF_Z_LSB", "BUF_Z_MSB",
					"PROD_REV", "WHO_AM_I",
					"SYS_MODE",
					"SENS_CONFIG1", "SENS_CONFIG2", "SENS_CONFIG3", "SENS_CONFIG4", "SENS_CONFIG5",
					"WAKE_IDLE _LSB", "WAKE_IDLE_MSB",
					"SLEEP_IDLE_LSB", "SLEEP_IDLE_MSB",
					"ASLP_COUNT_LSB", "ASLP_COUNT_MSB",
					"INT_EN", "INT_PIN_SEL",
					"OFF_X", "OFF_Y", "OFF_Z",
					"RESERVED_REG2",
					"BUF_CONFIG1", "BUF_CONFIG2",
					"ORIENT_STATUS", "ORIENT_CONFIG", "ORIENT_DBCOUNT", "ORIENT_BF_ZCOMP", "ORIENT_THS_REG",
					"SDCD_INT_SRC1", "SDCD_INT_SRC2",
					"SDCD_CONFIG1", "SDCD_CONFIG2",
					"SDCD_OT_DBCNT", "SDCD_WT_DBCNT",
					"SDCD_LTHS_LSB", "SDCD_LTHS_MSB",
					"SDCD_UTHS_LSB", "SDCD_UTHS_MSB",
					"SELF_TEST_CONFIG1", "SELF_TEST_CONFIG2",
					)

	def __init__( self, i2c, address = DEFAULT_ADDR ):
		"""
		Initializer for FXLS8974 class instance

		Parameters
		----------
		i2c		: I2C instance
		address	: int, option

		"""
		super().__init__( i2c, address )

		self.fs_range	= 2
		self.fullscale( self.fs_range )
		self.bit_operation( "SENS_CONFIG1", 0x01, 0x01 )

	def __three_axis( self, reg ):
		return unpack( "<hhh", self.read_registers( reg, 6, barray = True ) )
	
	def __xyz( self ):
		return [ (d << 4) / 2**15 * self.fs_range for d in self.three_axis( "OUT_X_LSB" ) ]	# convert to G

	def __fullscale( self, v ):
		if 16 <= v:
			setting	= 0x3
		elif 8 <= v:
			setting	= 0x2
		elif 4 <= v:
			setting	= 0x1
		else:
			setting	= 0x0
		
		self.bit_operation( "SENS_CONFIG1", 0x06, setting << 1 )


from machine	import	Pin, I2C
from utime		import sleep

def main():
	i2c		= I2C( 0, freq = (400 * 1000) )
#	acc		= FXOS8700( i2c )
	acc		= FXLS8974( i2c )

	print(	i2c.scan() )
	acc.dump_reg()

	while True:
#		xyz	= acc.xyz()
#		g	= sum( [ g * g for g in xyz ] ) ** 0.5
#		print( g, xyz )
#		print( acc.mag() )
#		print()
#		print( acc.six_axis() )
		print( acc.xyz() )
		sleep( 0.5 )
		
if __name__ == "__main__":
	main()
