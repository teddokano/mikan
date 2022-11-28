from	machine	import	Pin, I2C, SoftSPI, SPI
from	utime	import	sleep

from	nxp_periph	import	SPI_target

class SC16IS752( SPI_target ):
	RHR		= 0x00
	THR		= 0x00
	IER		= 0x01
	FCR		= 0x02
	IIR		= 0x02
	LCR		= 0x03
	MCR		= 0x04
	LSR		= 0x05
	MSR		= 0x06
	SPR		= 0x07
	TCR		= 0x06
	TLR		= 0x07
	TXLVL	= 0x08
	RXLVL	= 0x09
	IODir	= 0x0A
	IOState	= 0x0B
	IOIntEna	= 0x0C
	IOControl	= 0x0E
	EFCR	= 0x0F
	DLL 	= 0x00
	DLH		= 0x01
	EFR		= 0x02
	XON1	= 0x04
	XON2	= 0x05
	XOFF1	= 0x06
	XOFF2	= 0x07

	def __init__( self, interface, cs = 0 ):
		SPI_target.__init__( self, interface, cs )

		self.reg_access( SC16IS752.LCR, 0, 0x80 );
		self.reg_access( SC16IS752.DLL, 0, 0x60 );
		self.reg_access( SC16IS752.DLH, 0, 0x00 );

		self.reg_access( SC16IS752.LCR, 0, 0xBF );
		self.reg_access( SC16IS752.EFR, 0, 0x10 );	# enable enhanced functions

		self.reg_access( SC16IS752.LCR, 0, 0x03 );	# word length R/W bit 1 and 0
		self.reg_access( SC16IS752.MCR, 0, 0x04 );	# TCR and TLR enable

	def reg_access( self, reg, ch, val ):
		self.send( [ (reg << 3 | ch << 1), val ] )

def main():
	spi	= SPI( 0, 1000 * 1000, cs = 0 )
	br	= SC16IS752( spi )

	while True:
		print( "#" )
		br.write_registers( SC16IS752.THR << 3, 0xAA )
		sleep( .01 )
		br.write_registers( SC16IS752.THR << 3, 0x55 )
		sleep( .01 )

if __name__ == "__main__":
	main()
