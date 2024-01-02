from	machine		import	SPI
from	nxp_periph	import	NAFE13388

spi	= SPI( 0, 1000_000, cs = 0, phase = 1 )

afe	= NAFE13388( spi, None )
afe.dump( [ 0x7C, 0x7D, 0x7E, 0xAE, 0xAF, 0x34, 0x37, None, 0x30, 0x31 ] )

count	= 0

afe.periodic_measurement_start()

while True:
	if afe.done:
		afe.done	= False
		print( f"{count},  {afe.ch[ 0 ]} μV,  {afe.ch[ 1 ]} μV" )
		count	+= 1
