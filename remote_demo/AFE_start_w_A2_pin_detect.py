from machine  import Pin
from demo_lib import demo
from utime    import sleep

def main():
	setting_detect	= Pin( "A2", Pin.IN )
	
	if setting_detect.value():
		demo( AFE_demo = True )
	else:
		demo( ip = (	"10.0.0.99", 		#	IP address
						"255.255.255.0", 	#	Subnet mask
						"10.0.0.1", 		#	Gateway
						"0.0.0.0" 			#	DNS
					), 
					AFE_demo = True 
			)

if __name__ == "__main__":
	main()
