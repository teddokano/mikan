import	machine
import	os

class DUT_base():
	SIG	= """\
		<b><a href="https://github.com/teddokano/mikan" target="_blank" rel="noopener noreferrer">mikan: I²C/SPI peripheral device drivers and demo</a><br/>
		{% mcu %}<br/>
		0100111101101011011000010110111001101111
		"""
	def __init__( self, dev ):
		self.page_data	= {}
		self.page_data[ "signature"   ]	= self.page_signature()

		if dev is None:
			return
	
		self.interface	= dev.__if
		self.dev		= dev
		self.type		= self.dev.__class__.__name__

		if isinstance( self.interface, machine.I2C ) or isinstance( self.interface, machine.SoftI2C ):
			self.address	= dev.__adr
			self.dev_name	= self.type + "_on_I2C(0x%02X)" % (dev.__adr << 1)
		else:
			self.address	= dev.__cs
			self.dev_name	= self.type + "_on_SPI({})".format( dev.__cs )

		self.page_data[ "dev_name"    ]	= self.dev_name
		self.page_data[ "class_name"  ]	= self.__class__.__name__
		self.page_data[ "dev_type"    ]	= self.type
		self.page_data[ "dev_link"    ]	= '<a href="{}" target="_blank" rel="noopener noreferrer">{}</a>'.format( self.DS_URL[ self.type ], self.type )
		self.page_data[ "dev_info"    ]	= self.dev.info()

	def load_html( self ):
		with open( "demo_lib/" + self.__class__.__name__ + ".html", "r" ) as f:
			html	= f.read()
		
		for key, value in self.page_data.items():
			html = html.replace('{% ' + key + ' %}', value )
		
		return html
	
	def page_signature( self ):
		return self.SIG.replace('{% mcu %}', "HTTP server on " + os.uname().machine + " / MicroPython version: " + os.uname().release )
		
	def load_file( self, file_name ):
		try:
			with open( file_name ) as f:
				s	= f.read()
		except:
			s	= ""	
		
		return s
