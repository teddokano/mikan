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

def main():
	print( MikanUtil.get_timer_id( 0 ) )
	print( MikanUtil.get_timer_id( 1 ) )
	print( MikanUtil.get_timer_id( 2 ) )

if __name__ == "__main__":
	main()
