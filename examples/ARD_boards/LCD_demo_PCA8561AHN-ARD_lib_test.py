from	machine		import	I2C
from	utime		import	sleep	
from	nxp_periph	import	PCA8561

i2c		= I2C( 0, freq = (400 * 1000) )
lcd	= PCA8561( i2c )

lcd.write_registers( "Display_ctrl_1", 0x01 )
lcd.write_registers( "COM0_07_00", [ 0xFF ] * 12 )
sleep( 0.5 )
lcd.write_registers( "COM0_07_00", [ 0x00 ] * 12 )

for c in range( 4 ):
	for s in range( 18 ):
		lcd.com_seg( c, s, 1 )
		sleep( 0.1 )

for c in range( 4 ):
	for s in range( 18 ):
		lcd.com_seg( c, s, 0 )
		sleep( 0.1 )

test	= [ chr( i ) for i in range( ord( "0" ), ord( "9" ) + 1 ) ]
test	= [ ".", "'", "+" ] + [ "-", "\\", "|", "/" ] * 5
test	= [ chr( i ) for i in range( ord( "A" ), ord( "Z" ) + 1 ) ]

while True:
	lcd.puts( "    test    ", char_per_sec = 4 )	#	will be converted to uppercase

	for i in range( 10000 ):
		lcd.puts( "{:4}".format( i ) )

	sleep( 0.5 )
	lcd.clear()

	for c in test:
		lcd.putchar( c )
		sleep( 0.2 )

	sleep( 0.5 )
	lcd.clear()
