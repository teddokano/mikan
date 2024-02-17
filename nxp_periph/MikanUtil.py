import	os
import	ure

class MikanUtil:
	"""
	MikanUtility class
	"""

	@classmethod
	def get_sys_rel( self ):
		"""
		register bit set/clear
	
		Returns
		-------
		str		: return value of os.uname().sysname
		float	: return value of os.uname().release. major.minor part in float

		"""

		rs	= ure.compile( r"^(.*\..*)\..*" )

		return os.uname().sysname, float( rs.match( os.uname().release ).group( 1 ) )

	@classmethod
	def get_timer_id( self, num ):
		"""
		showing register name, address/pointer and value

		Parameters
		----------
		num : int
			timer ID candidate

		Returns
		-------
		int	: Timer ID which is required for the board
		"""
		
		sys, rev	= self.get_sys_rel()
		
		if "mimxrt" == sys and rev < 1.20:
			return num
		else:
			return -1

class BusInOut():
	from	machine		import	Pin
	
	def __init__( self, pin_labels ):
		self.pins	= []
		
		for label in pin_labels:
			self.pins	+= [ Pin( label, Pin.IN ) ] if label else None

		self.pins	= self.pins[::-1]

	def config( self, mode = Pin.IN, pull = None ):
		print( "CONFIG" )

		for pin in self.pins:
			if pin:
				pin.init( mode = mode, pull = pull )

	def input( self ):
		self.config( Pin.IN )
		
	def output( self ):
		self.config( Pin.OUT )
	
	def value( self, v = None ):
		if v is None:
			r	= 0;
			for i, pin in enumerate( self.pins ):
				r	|= (pin.value() if pin else 0) << i
			return r
		else:
			for i, pin in enumerate( self.pins ):
				pin.value( v & (0x1 << i) )
			
	@property
	def v( self ):
		return self.value()

	@v.setter
	def v( self, v ):
		self.value( v )

		
def test_BusInOut():
	from	utime		import	sleep_ms

	busout	= BusInOut( [ "D7", "D6", "D5", "D4", "D3", "D2", "D1", "D0" ] )
	#busout	= BusInOut( [ "D7", "D6", "D5", "D4", "D3", "D2", "D1", "D0" ][::-1] )
	busin	= BusInOut( [ "D15", "D14", "D13", "D12", "D11", "D10", "D9", "D8" ] )
	busout.output()
	busin.input()
	
	count	= 0
	
	while True:
#		busout.value( count & 0xFF )
		busout.v	= count & 0xFF
		count+= 1
		
		print( f"0x{busin.v:02X}" )
		sleep_ms( 1 )

def test_get_timer_id():
	print( MikanUtil.get_timer_id( 0 ) )
	print( MikanUtil.get_timer_id( 1 ) )
	print( MikanUtil.get_timer_id( 2 ) )

def main():
	test_BusInOut()

if __name__ == "__main__":
	main()
