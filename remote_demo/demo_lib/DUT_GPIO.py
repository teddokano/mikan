import	machine
import	ure
import	ujson

from	nxp_periph	import	PCA9554, PCA9555, PCAL6408, PCAL6416, PCAL6524, PCAL6534, 
from	nxp_periph	import	GPIO_base
from	demo_lib	import	DUT_base

class DUT_GPIO( DUT_base.DUT_base ):
	APPLIED_TO	= GPIO_base
	prev_r		= []
	DS_URL		= { 
						"PCA9554": "https://www.nxp.jp/docs/en/data-sheet/PCA9554_9554A.pdf",
						"PCA9555": "https://www.nxp.com/docs/en/data-sheet/PCA9555.pdf",
						"PCAL6408": "https://www.nxp.com/docs/en/data-sheet/PCAL6408A.pdf",
						"PCAL6416": "https://www.nxp.com/docs/en/data-sheet/PCAL6416A.pdf",
						"PCAL6524": "https://www.nxp.com/docs/en/data-sheet/PCAL6524.pdf",
						"PCAL6534": "https://www.nxp.com/docs/en/data-sheet/PCAL6534.pdf",
					}

	regex_reg	= ure.compile( r".*reg=(\d+)&val=(\d+)" )

	def __init__( self, dev ):
		super().__init__( dev )
		self.info		= [ "General Purpose IO expander", "" ]
		self.symbol		= '↕'
		

	def parse( self, req ):
		if self.dev_name not in req:
			return None
	
		if "?" not in req:
			return self.page_setup()
		elif "allreg" in req:
			return 'HTTP/1.0 200 OK\n\n' + ujson.dumps( { "reg": self.dev.dump() } )
		elif "ping" in req:
			reg			= self.dev.dump()
			result		= 0 if (self.prev_r == reg) else 1
			self.prev_r	= reg
			return 'HTTP/1.0 200 OK\n\n' + ujson.dumps( { "result": result } )
		else:
			m	= self.regex_reg.match( req )
			if m:
				idx	= int( m.group( 1 ) )
				val	= int( m.group( 2 ) )
				
				self.dev.write_registers( self.dev.REG_LIST[ idx ][ "name" ], val )
				return 'HTTP/1.0 200 OK\n\n' + ujson.dumps( { "reg": self.dev.REG_LIST[ idx ][ "idx" ], "val": val } )
			else:
				return self.sending_data()

	def sending_data( self ):
		return 'HTTP/1.0 200 OK\n\n'

	def page_setup( self ):
		self.page_data[ "symbol"    ]	= self.symbol
		self.page_data[ "reg_table" ]	= self.get_reg_table( 4 )

		return self.load_html()

	def get_reg_table( self, cols ):
		total	= len( self.dev.REG_LIST )
		rows	= (total + cols - 1) // cols

		s	 	= [ '<table class="table_RTC">' ]

		for y in range( rows ):
			s	 	+= [ '<tr class="reg_table_row">' ]
			for i in range( y, total, rows ):
				ri	= self.dev.REG_LIST[ i ][ "idx" ]
				rn	= self.dev.REG_LIST[ i ][ "name" ]

				s	+= [ '<td class="td_RTC reg_table_name">{}</td><td class="td_RTC reg_table_val">0x{:02X}</td>'.format( rn, ri ) ]
				s	+= [ '<td class="td_RTC reg_table_val"><input type="text" onchange="updateRegField( {} )" id="regField{}" minlength=2 size=2 value="--" class="regfield"></td>'.format( i, i ) ]

			s	+= [ '</tr>' ]

		s	+= [ '</table>' ]
		return "\n".join( s )
