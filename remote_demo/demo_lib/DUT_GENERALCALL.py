from	nxp_periph	import	I2C_target

class GENERAL:
	pass

class General_call( GENERAL, I2C_target ):
	def __init__( self, i2c ):
		super().__init__( i2c, 0 )
		
	def reset( self ):
		self.live	= True
		self.write_registers( 0x06, [] )

	def reprogram( self ):
		self.live	= True
		self.write_registers( 0x04, [] )


class DUT_GENERALCALL():
	"""
	This is a special class to implement "I2C general call" feature.
	This class doesn't have html page.
	"""
	APPLIED_TO	= GENERAL
	dev_name	= "GENERAL"
	
	def __init__( self, dev ):
		self.interface	= dev.__if
		self.dev		= General_call( self.interface )
		self.type		= self.dev.__class__.__name__
		self.info		= [ "General call", "" ]
		self.address	= dev.__adr

	def parse( self, req ):
		if self.dev_name not in req:
			return None
	
		if "reset" in req:
			print( "********** General call: Software reset **********" )
			self.dev.reset()
		elif "reprogram" in req:
			print( "********** General call: reprogram **********" )
			self.dev.reprogram()

		return 'HTTP/1.0 200 OK\n\n'	# dummy

