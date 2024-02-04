# "mikan/remote_demo" 🍊
A demo code for mikan.  
This demonstration works with a network connection. The microcontroller performs a HTTP server to provide user interface on web browsers.  

```
Peripheral_devices <---------> Mictocontroller_board <-----> PC(web-browser)
                    (I²C/SPI)                         (LAN)
```

## Install

Installation can be done by manual file copy into the microcontroller performs storage or by using `mip` with `mpremote`.  

### Manual install

You may already installed mikan driver in your microcontroller board.  
On addition to that, a folder is needed to be copied into the board. 
It is `remote_demo/demo_lib` folder. The `demo_lib` should be copied in **module serch path**.  
In case of the **MIMXRT1050-EVKB** and **MIMXRT1170-EVK**, it can be copied under `/flash` folder. 
So, after installation, the board will have folders like...
```
/flash/lib/nxp_periph/
/flash/demo_lib/
```

### Install by `mip` with `mpremote`

If the `mpremote` is installed on PC, the install can be done by terminal command.   
To install the _**remote_demo**_, type next command. This command overwrites 'mikan' class driver under `/flash/nxp_periph/` if it have been already installed.  

```
mpremote mip install github:teddokano/mikan/remote_demo
```

## Give it a try!
`remote_demo/start_w_auto_IP(DHCP).py`, `remote_demo/start_w_fixed_IP.py` and `remote_demo/start_w_A2_pin_detect.py` are start scripts to run the demo.  
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

> **Note**  
> The **MIMXRT1170-EVK** has two Ethernet ports. Choose 1Gbps port for the network connection.  
> If you need to change the port to 100Mbps, a variable:`ep_num` should be edited in `remote_demo/demo_lib/DEMO.py`.   



### In DHCP environment

`remote_demo/start_w_auto_IP(DHCP).py` is a script to run the demo in network which can use DHCP. 
IP address will be given from DHCP server after the demo started. 

> **Note**  
> The **DHCP server** is a server which gives IP address to every devices in local network.  

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

### IP address setting change by pin state

`remote_demo/start_w_fixed_IP.py` is to run the demo with DHCP or fixed-IP. The DHCP or fixed-IP setting can be selected by `A2` pin state of MCU board's Arduino shueld socket.  
If the `A2` pin is HIGH (pulled-up), the demo will be started as DHCP. If it is LOW (tied to GND), fixed-IP setting will be applied.  

## Boot automatically

To run the demo automatically after turn-on or reset, one of those start script files can be stored in root of the MCU-board storage as `main.py`.  
With this setting, the demo works stand-alone. No start script run needed from PC.  
![main_py.png](https://github.com/teddokano/additional_files/blob/main/mikan/img/main_py.png)   
_The start script is copied in MCU-board storage root with remaning it as `main.py`_

## Video

This demonstration works with a network connection. The microcontroller performs a HTTP server to provide user interface on web browsers.  
Video is available --> [https://youtu.be/usPzhs_2IsI](https://youtu.be/usPzhs_2IsI)   
[![](https://github.com/teddokano/additional_files/blob/main/mikan/img/remo_demo_perform.png)](https://youtu.be/usPzhs_2IsI)
 

How to setup? --> [https://youtu.be/fkHqdnd4t1s](https://youtu.be/fkHqdnd4t1s)  
[![](https://github.com/teddokano/additional_files/blob/main/mikan/img/remo_demo_install.png)](https://youtu.be/fkHqdnd4t1s)

# AFE demo
**AFE demo** is an option setting of the **remote_demo**. 
A demo start script sample is available as `remote_demo/AFE_start_w_A2_pin_detect.py`.  
The script calls `demo()` finction with an option parameter of `config = "AFE"`. It starts the demo in AFE demo congiguration. 

💡⏰🌡️↕🔠🔄💁🍎🌊
