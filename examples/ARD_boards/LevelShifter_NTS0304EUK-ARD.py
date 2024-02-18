from	machine		import	Pin, I2C, SPI, ADC
from	utime		import	sleep
from	nxp_periph	import	AD5161, BusInOut

sel_I2C	= True	# set True for I2C demo, False for SPI demo

"""
NTS0304EUK-ARD jumper settings may need to be changed. 
* J8 and J9 pins 1-2, 3-4, 5-6, 7-8 are needed to be shorted. 
  Becareful that J8 and J9 directions are different
* J2 need to be removed to get device data
"""

"""
Arduino conector pin settings

"A2": SPI = 0, I2C = 1
"A3": 0 to route op-amp output to "A1"
"D5": 0 to Disconnect CS and set address 0x5A, 1 to connrct CS to AD5161
"""

setting	= BusInOut( [ "A2", "A3", "D5" ], output = True )
ldo1	= BusInOut( [ "D4", "D1", "D0" ], output = True )
ldo2	= BusInOut( [ "D3", "D2" ], output = True )
alt_spi	= BusInOut( [ "D6", "D7", "D8", "D9" ] )
adc		= ADC( Pin( "A0" ) )

if sel_I2C:
	setting.v	= 0b100
	s0			= ""
	pot			= AD5161( I2C( 0, freq = (400_000) ) )
else:
	setting.v	= 0b001
	s0			= "(previous value)"
	pot			= AD5161( SPI( 0, 1000_000, cs = 0 ) )

v1_values = [ 1.2, 1.8, 2.5, 3.3, 0.95 ]
v2_values = [ 1.8, 2.5, 3.3, 4.96]

while True:
	for v1 in range( 5 ):
		ldo1.v	= v1
		for v2 in range( 4 ):
			ldo2.v	= v2
			
			if v1_values[ v1 ] > v2_values[ v2 ]:
				continue
				
			print(
				"New voltages are set: LDO1 = {}V, LDO2 = {}V".format(
					v1_values[v1], v2_values[v2]
				)
			)
			sleep(1)
		
			for i in range( 256 ):
				if sel_I2C:
					pot.value( i )
					rb	= pot.value()
				else:
					rb	= pot.value( i )
					
				ad	= 3.3 * adc.read_u16() / 65536
				print( f"sent: {i:3}  read back{s0}: {rb:3}  output voltage: {ad:4.2f}V", end = "\r" )
				sleep( 0.005 )

			print( "" )
			print( "" )
