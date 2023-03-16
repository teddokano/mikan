from demo_lib import demo

def main():
	demo( ip = (	"10.0.0.99", 		#	IP address
					"255.255.255.0", 	#	Subnet mask
					"10.0.0.1", 		#	Gateway
					"0.0.0.0" 			#	DNS
					)
				)

if __name__ == "__main__":
	main()
