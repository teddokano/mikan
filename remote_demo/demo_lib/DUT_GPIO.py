import	machine
import	ure
import	ujson

from	nxp_periph	import	PCA9554, PCA9555, PCAL6408, PCAL6416, PCAL6524, PCAL6534, 
from	nxp_periph	import	GPIO_base
from	demo_lib	import	DUT_base

class DUT_GPIO( DUT_base.DUT_base ):
	APPLIED_TO	= GPIO_base
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
		self.info		= [ "General Purpose IO expander", "{}bits".format( self.dev.N_BITS ) ]
		self.symbol		= '↕'
		

	def parse( self, req ):
		if self.dev_name not in req:
			return None
	
		if "?" not in req:
			return self.page_setup()
		elif "allreg" in req:
			return ujson.dumps( { "reg": self.dev.dump(), "bf_reg": self.bf_reg } )
		elif "reglist" in req:
			return ujson.dumps( { "reglist": self.dev.REG_LIST } )
		else:
			m	= self.regex_reg.match( req )
			if m:
				idx	= int( m.group( 1 ) )
				val	= int( m.group( 2 ) )
				
				self.dev.write_registers( self.dev.REG_LIST[ idx ][ "name" ], val )
				return ujson.dumps( { "reg": self.dev.REG_LIST[ idx ][ "idx" ], "val": val } )
			else:
				return ""

	def page_setup( self ):
		self.page_data[ "symbol"    ]	= self.symbol
		self.page_data[ "reg_table" ]	= self.get_reg_table( 4 )
		self.page_data[ "bit_table" ]	= self.get_bit_table()

		return self.load_html()

	def get_reg_table( self, cols ):
		total	= len( self.dev.REG_LIST )
		rows	= (total + cols - 1) // cols

		s	 	= [ '<table class="table_GPIO">' ]

		for y in range( rows ):
			s	 	+= [ '<tr class="reg_table_row">' ]
			for i in range( y, total, rows ):
				ri	= self.dev.REG_LIST[ i ][ "idx" ]
				rn	= self.dev.REG_LIST[ i ][ "name" ]

				s	+= [ '<td class="td_GPIO reg_table_name">{}</td><td class="td_GPIO reg_table_name">0x{:02X}</td>'.format( rn, ri ) ]
				s	+= [ '<td class="td_GPIO reg_table_val"><input type="text" onchange="updateRegField( {} )" id="regField{}" minlength=2 size=2 value="--" class="regfield"></td>'.format( i, i ) ]

			s	+= [ '</tr>' ]

		s	+= [ '</table>' ]
		return "\n".join( s )

	def get_bit_table( self ):
		attr_list	= [ "__in", "__out", "__pol", "__cfg", "__im", "__is", "__pe", "__ps" ]
		rn_list		= [ getattr( self.dev, a ) for a in attr_list if hasattr( self.dev, a ) ]
		rlist		= [ n[ "name" ] for n in self.dev.REG_LIST ]
		
		self.bf_reg		= []

		s	= [ '<table class="table_GPIO">' ]

		s	+= [ '<tr class="reg_table_row">' ]
		s	+= [ '<td class="td_GPIO_PORT_1 reg_table_name">port</td>' ]
		for i in range( self.dev.N_PORTS ):
			s	+= [ '<td class="td_GPIO_PORT_{} reg_table_name" colspan="8">{}</td>'.format( i % 2, i ) ]
		s	+= [ '</tr>' ]

		s	 += [ '<tr class="reg_table_row">' ]
		s	 += [ '<td class="td_GPIO_BIT_1 reg_table_name">bit</td>' ]
		for i in range( self.dev.N_PORTS ):
			for j in range( 8 ):
				s	+= [ '<td class="td_GPIO_BIT_{} reg_table_name">{}</td>'.format( i % 2, 7 - j ) ]
		s	+= [ '</tr>' ]

		for n, r in enumerate( rn_list ):
			ri_base	= rlist.index( r )
			s	+= [ '<tr class="reg_table_row">' ]
			s	+= [ '<td class="td_GPIO_BF_name{} reg_table_name">{}</td>'.format( n % 2, r.replace( " 0", "" ) ) ]

			for p in range( self.dev.N_PORTS ):
				ri	= ri_base + p
				self.bf_reg	+= [ ri ]
				
				for i in range( 8 ):
					bi	= 7 - i
					s	+= [ '<td class="td_GPIO_BF_{}{} reg_table_val"><input type="text" onchange="updateBitField( {}, {} )" id="bitField{}-{}" minlength=1 size=1 value="-" class="regfield"></td>'.format( n % 2, i // 4, ri, bi, ri, bi ) ]
			s	+= [ '</tr>' ]

		s	+= [ '</table>' ]

		return "\n".join( s )
