from nxp_periph.interface	import	I2C_target
from machine		import	Pin, I2C
from utime import sleep
from ustruct import unpack

def main():
	i2c		= I2C( 0, freq = (400 * 1000) )
	acc		= FXOS8700( i2c )

	print( 	i2c.scan() )
	acc.dump_reg()

	while True:
		print( acc.xyz() )
		print( acc.mag() )
		print()
		sleep( 0.5 )

class FXOS8700( I2C_target ):
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
		super().__init__( i2c, address )
		
		self.write_registers( "F_SETUP", 0x00 )
		self.write_registers( "CTRL_REG1", 0x01 )
		self.write_registers( "M_CTRL_REG1", 0x03 )

	def three_axis( self, reg ):
		return unpack( ">hhh", self.read_registers( reg, 6, barray = True ) )
	
	def xyz( self ):
		return self.three_axis( "OUT_X_MSB" )

	def mag( self ):
		return self.three_axis( "M_OUT_X_MSB" )
		
if __name__ == "__main__":
	main()
