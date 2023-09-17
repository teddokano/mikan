from	machine		import	I2C
from	nxp_periph	import	PCAL6524, PCAL6534
import	utime

i2c		= I2C( 0, freq = (400 * 1000) )

gpio	= PCAL6524( i2c, setup_EVB = True )
#gpio	= PCAL6534( i2c, setup_EVB = True )

if gpio.N_PORTS is 3:
	io_config_and_pull_up	= [ 0x00, 0x00, 0xF0 ]
elif gpio.N_PORTS is 5:
	io_config_and_pull_up	= [ 0x00, 0x00, 0x00, 0xE0, 0x03 ]

gpio.config		= io_config_and_pull_up
gpio.pull_up	= io_config_and_pull_up
gpio.mask		= [ ~v for v in io_config_and_pull_up ]
gpio.pull_en	= [ 0xFF ] * gpio.__np

count	= 0

while True:
	gpio.value	= [ count ] * 3
	count		= (count + 1) & 0xFF
	
	r	= gpio.value
	print( "port read = {}".format( [ "0b{:08b}".format( i ) for i in r ] ), end = "\r" )
