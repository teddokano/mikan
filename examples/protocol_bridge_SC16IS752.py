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

		self.reg_access( self.LCR, 0, 0x80 );	# 0x80 to program baud rate
		self.reg_access( self.DLL, 0, 0x60 );
		self.reg_access( self.DLH, 0, 0x00 );
		print( self.reg_access( self.LCR, 0 ) )
		print( self.reg_access( self.DLL, 0 ) )
		print( self.reg_access( self.DLH, 0 ) )


		self.reg_access( self.LCR, 0, 0xBF );
		self.reg_access( self.EFR, 0, 0x10 );	# enable enhanced functions

		self.reg_access( self.LCR, 0, 0x03 );	# 8 data bit, 1 stop bit, no parity
		self.reg_access( self.FCR, 0, 0x06 );	# reset TXFIFO, reset RXFIFO, non FIFO mode
		self.reg_access( self.FCR, 0, 0x01 );	# enable FIFO mode
		
	def reg_access( self, *args ):
		n_args	= len( args )
		if n_args is 2:
			return self.receive( [ 0x80 | (args[ 0 ] << 3 | args[ 1 ] << 1), 0xFF ] )[ 1 ]
		elif n_args is 3:
			self.send( [ (args[ 0 ] << 3 | args[ 1 ] << 1), args[ 2 ] ] )
		else:
			print( "reg_access error" )

	def reg_access_old( self, reg, ch, val ):
		self.send( [ (reg << 3 | ch << 1), val ] )

def main():
	spi	= SPI( 0, 1000 * 1000, cs = 0 )
	br	= SC16IS752( spi )

	while True:
		#print( "#" )
		br.write_registers( br.THR << 3, 0xAA )
		sleep( .01 )
		br.write_registers( br.THR << 3, 0x55 )
		sleep( .01 )

if __name__ == "__main__":
	main()
