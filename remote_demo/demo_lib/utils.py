#	MicroPython HTTP server sample code based on "http_server_simplistic.py".
#	https://github.com/micropython/micropython/blob/master/examples/network/http_server_simplistic.py
#
#	Tedd OKANO / Released under the MIT license
#	29-Oct-2022
#	version	0.1

import	os

def file_loading( str, files_list ):
	print( os.getcwd() )
	print( os.listdir() )

	for k, file_names in files_list.items():
		s	= ""
		print( k )
		for fn in file_names:
			print( fn )
			jsf	 = open( fn + "." + k )
			s	+= jsf.read() + "\n"
			jsf.close

		print( k )
		str = str.replace( "{% " + k + " %}", s )

	return str
