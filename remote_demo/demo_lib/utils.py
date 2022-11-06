#	MicroPython HTTP server sample code based on "http_server_simplistic.py".
#	https://github.com/micropython/micropython/blob/master/examples/network/http_server_simplistic.py
#
#	Tedd OKANO / Released under the MIT license
#	29-Oct-2022
#	version	0.1

import	os

def file_loading( str, files_list ):
	#	using list instead of dict because current MicroPython's dict cannot keep key order
	#print( os.getcwd() )
	#print( os.listdir() )

	for category in files_list:
		k			= category[ 0 ]
		file_names	= category[ 1: ]

		s	= ""
		
		#print( "file category : {}".format( k ) )
		for fn in file_names:
			#print( "  loading file : {}".format( k ) )
			jsf	 = open( fn + "." + k )
			s	+= jsf.read() + "\n"
			jsf.close

		str = str.replace( "{% " + k + " %}", s )

	return str
	
def file_loading_using_dict_version( str, files_list ):
	#print( os.getcwd() )
	#print( os.listdir() )

	for k, file_names in files_list.items():
		s	= ""
		#print( "file category : {}".format( k ) )
		for fn in file_names:
			#print( "  loading file : {}".format( k ) )
			jsf	 = open( fn + "." + k )
			s	+= jsf.read() + "\n"
			jsf.close

		str = str.replace( "{% " + k + " %}", s )

	return str

def page_signature():
	s	= """\
		<b><a href="https://github.com/teddokano/mikan" target="_blank" rel="noopener noreferrer">mikan: I²C/SPI peripheral device drivers and demo</a><br>
		HTTP server on<br/>
		{% mcu %}</b><br/>
		0100111101101011011000010110111001101111
		"""
	
	return s.replace('{% mcu %}', os.uname().machine )
	
