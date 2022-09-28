from	machine	import	I2C
from	utime	import	sleep
import	math

from	nxp_periph	import	PCA9955B

def demo( led_ctlr ):
	EVB16	= True if led_ctlr.__class__.__name__ == "PCA9955B" else False

	SAMPLE_LENGTH	= 60
	COLORS			= 3
	N_LED_UNIT		= led_ctlr.CHANNELS // (COLORS + (1 if EVB16 else 0))

	print( "test_harness_0 working N_LED_UNIT={}".format( N_LED_UNIT ) )

	pattern	= [ 0.5 - 0.5 * math.cos( 2 * math.pi * x / SAMPLE_LENGTH ) for x in range( SAMPLE_LENGTH ) ]
	pattern	= [ int( x * x * 255.0 ) for x in pattern ]
	ch_ofst	= SAMPLE_LENGTH // N_LED_UNIT

	white_val	= 0x00
	while True:
		if EVB16:
			white_val	= 0xFF if white_val == 0x00 else 0x00

			led_ctlr.pwm(  0,  white_val )
			led_ctlr.pwm(  8,  white_val )
			led_ctlr.pwm(  4, ~white_val )
			led_ctlr.pwm( 12, ~white_val )

		for lum in range( SAMPLE_LENGTH ):
			for col in range( COLORS ):
				for n in range( N_LED_UNIT ):
					target_ch	= col + n * (led_ctlr.CHANNELS // N_LED_UNIT) +  (1 if EVB16 else 0)
					value		= pattern[ (lum + col * (SAMPLE_LENGTH // 3) + n * N_LED_UNIT) % SAMPLE_LENGTH ]
					led_ctlr.pwm( target_ch, value )
			sleep( 0.02 )



def main():
	i2c		= I2C( 0, freq = (400 * 1000) )
	led_c	= PCA9955B( i2c )
	demo( led_c )


if __name__ == "__main__":
	main()
