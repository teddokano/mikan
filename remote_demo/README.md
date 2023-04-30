# "mikan/remote_demo" 🍊
A demo code for mikan.  
This demonstration works with a network connection. The microcontroller performs a HTTP server to provide user interface on web browsers.  

```
Peripheral_devices <---------> Mictocontroller_board <-----> PC(web-browser)
                    (I²C/SPI)                         (LAN)
```

## Install
You may already installed mikan driver in your microcontroller board.  
On addition to that, a folder is needed to be copied into the board. 
It is `remote_demo/demo_lib` folder. The `demo_lib` should be copied in **module serch path**.  
In case of the MIMXRT1050-EVKB, it can be copied under `/flash` folder. 
So, after installation, the board will have folders like...
```
/flash/lib/nxp_periph/
/flash/demo_lib/
```

## Give it a try!
`remote_demo/start_w_auto_IP(DHCP).py` and `remote_demo/start_w_fixed_IP.py` are start scripts to run the demo.  
Choose one of them and run. 

For network setup, user can choose both of these options: 
- Join to existing network
```

Internet <---> Router(DHCP server)
                  |
                  +  <---> PC
                  |
                  +  <---> microcontroller_board(mikan)
                  |
                  +  <---> Other_devices
```
- Direct PC connection
```
PC <---> microcontroller_board(mikan)
```

### In DHCP environment

`remote_demo/start_w_auto_IP(DHCP).py` is a script to run the demo in network which can use DHCP. 
IP address will be given from DHCP server after the demo started. 

> **Note**
The **DHCP server** is a server which gives IP address to every devices in local network.  

When your microcontroller board is connected existing network, you may try this. If the DHCP is not working, the demo will show an error message as below and the board will keep to repeat blinking LED 3 times. 

```
remote device demo
  http server is started working on i.MX RT1050 EVKB-A1 with MIMXRT1052DVL6B

...
..
starting network
ethernet port 0 is activated
**** ERROR ****
**** ERROR ****
**** ERROR ****
Can't get/set IP address. Tried to set dhcp. OSError:('timeout waiting for DHCP to get IP address',)
```

### To use fixed IP address like direct connection with an Ethernet cable
`remote_demo/start_w_fixed_IP.py` is to run the demo with fixed IP address. 
This can be used for network setting like direct microcontroller board and PC with an Ethernet cable. 
When you use direct connection to the PC, please set the PC's Ethernet port properlly (IP address and subnet mask).  
 
If you are using in existing network without DHCP, you may need to edit to adapt your environment. 
The code will be looked like below. Edit **IP address**, **Subnet mask**, **Gateway** and **DNS** to fit your network environment. 

```python
from demo_lib import demo

def main():
    demo( ip = (    "10.0.0.99",        # IP address
                    "255.255.255.0",    # Subnet mask
                    "10.0.0.1",         # Gateway
                    "0.0.0.0"           # DNS
               )
		)

if __name__ == "__main__":
    main()
```

## Video

This demonstration works with a network connection. The microcontroller performs a HTTP server to provide user interface on web browsers.  
Video is available --> [https://youtu.be/usPzhs_2IsI](https://youtu.be/usPzhs_2IsI)   
[![](https://github.com/teddokano/additional_files/blob/main/mikan/img/remo_demo_perform.png)](https://youtu.be/usPzhs_2IsI)
 

How to setup? --> [https://youtu.be/fkHqdnd4t1s](https://youtu.be/fkHqdnd4t1s)  
[![](https://github.com/teddokano/additional_files/blob/main/mikan/img/remo_demo_install.png)](https://youtu.be/fkHqdnd4t1s)

💡⏰🌡️↕🔠🔄💁🍎
