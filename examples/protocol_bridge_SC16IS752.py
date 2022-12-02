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

	def __init__( self, interface, cs = 0, channel = 0, osc = 14746500, baud = 9600 ):
		SPI_target.__init__( self, interface, cs )

		self.osc	= osc
		self.ch		= channel
		self.baud( baud )

		self.reg_access( self.LCR, 0xBF )
		self.reg_access( self.EFR, 0x10 )	# enable enhanced functions

		self.reg_access( self.LCR, 0x03 )	# 8 data bit, 1 stop bit, no parity
		self.reg_access( self.FCR, 0x06 )	# reset TXFIFO, reset RXFIFO, non FIFO mode
		self.reg_access( self.FCR, 0x01 )	# enable FIFO mode

		print( "MCR:0x{:02X}".format( self.reg_access( self.MCR ) ) )
		print( "LSR:0x{:02X}".format( self.reg_access( self.LSR ) ) )

	def baud( self, baud ):
		lcr	= self.reg_access( self.LCR )
		divisor	= int( self.osc / (baud * 16) )
		print( divisor )

		self.reg_access( self.LCR, 0x80 )	# 0x80 to program baud rate
		self.reg_access( self.DLL, divisor & 0xFF )
		self.reg_access( self.DLH, divisor >> 8 )
		
		print( divisor )

		self.reg_access( self.LCR, lcr )
		
	def reg_access( self, *args ):
		n_args	= len( args )
		if n_args is 1:
			return super().receive( [ 0x80 | (args[ 0 ] << 3 | self.ch), 0xFF ] )[ 1 ]
		elif n_args is 2:
			super().send( [ (args[ 0 ] << 3 | self.ch), args[ 1 ] ] )
		else:
			print( "reg_access error" )

	def tx_buffer_empty( self ):
		return self.reg_access( self.LSR ) & 0x20

	def wait_tx_ready( self ):
		while not self.tx_buffer_empty():
			pass

	def send( self, data ):
		print( "sending" )
		if isinstance( data, int ):
			print( "it's int" )
			data	= [ data ]
		elif isinstance( data, str ):
			print( "it's str" )
			data	= list( data )
			data	= [ ord( i ) for i in data ]
		
		for d in data:
			self.wait_tx_ready()		
			self.reg_access( self.THR, d )

	def receive_check( self ):
		pass
		
	def receive_check2( self ):
		if ( self.reg_access( self.LSR ) & 0x01 ):
			print( "got data" )
		else:
			print( "no data" )
		
		print( self.reg_access( self.RHR ) )
	

def main():
	spi	= SPI( 0, 1000 * 1000, cs = 0 )
	br	= SC16IS752( spi )
	
	br.baud( 9600 )
	print( "" )
	
	while True:
		#print( "#" )
		br.send( 0xAA )
		br.receive_check()
		br.receive_check()
		br.send( 0x55 )
		br.send( [ x for x in range( 8 ) ] )
		br.send( "abcdefg" )
		br.receive_check()
		br.receive_check()

if __name__ == "__main__":
	main()
