AFE demo suitcase User manual

# What is this? 
The AFE demo suitcase is a demoset of NAFE13388 (Analog Front-End: AFE) and i.MX RT1050 (closs-over microcontroller: cross-over MCU) to perform precise analog voltage measurement. 
This suitcase including 2 sensors of thermo-couple and load-cell. The system shows its analog performance by measurering small voltages from those sensors. 

The software runs on an interpreter called MicroPython on the i.MX RT1050. The MicroPython is a Python3 compatible software environment available on MCUs. 
The software performs control and data read form the AFE and web-server to provide data to a remote device.  
This demo code is available as open source distributed with MIT license. 

![overview](https://github.com/teddokano/mikan/blob/afe/remote_demo/references/pics/overview.jpeg)


## Ingredients (hardware/software blocks)
### Hardware
This demo is including following boards and devices. 
- NAFE13388-EVB
- MIMXRT1050-EVKB
- Arduino adapter board between NAFE13388-EVB MIMXRT1050-EVKB
- Thermo-couple (K type)
- Load-cell (2kg max)
- Wi-Fi access point
- USB hub (as a 5V supply)
- Small character LCD (on Wi-Fi access point)
- 24V AC adapter (for NAFE13388-EVB power supply)
- 5V AC adapter (for MIMXRT1050-EVKB power supply)

![top_view](https://github.com/teddokano/mikan/blob/afe/remote_demo/references/pics/top_view.png)  

![hardware_blocks](https://github.com/teddokano/mikan/blob/afe/remote_demo/references/pics/hardware_blocks.png)

### Software
'mikan' class-libraries and demo code for AFE demo.  
Code is available on https://github.com/teddokano/mikan/tree/afe ('afe' branch on 'mikan' repository)

![software_blocks](https://github.com/teddokano/mikan/blob/afe/remote_demo/references/pics/software_blocks.png)

## Remote device requirements
For the access to the demo suitecase, a web-browser is required. User can use any modern web-browsers like Chrome, FireFox and Safari.  
Please make sure to use latest version of those browsers.  
As far as the web-browser works, user can use any hardware devices. It can be PC, tablet and smartphone. 
For PC, user can use wireless and wired connection. 

# Getting started
## Procedure of turning-ON (Wi-Fi operation)
#### (1) Secure connections of boards and cables
After open the box, please make sure the boards and cables securely connected.  
The boards of AFE, adapter and MCU could be floating after porting. The connectors of DC input on AFE, USB and LAN-cable could be loose after transpotation.  

#### (2) Jumper setting for DHCP
The Wi-Fi access point performs DHCP server to allocate IP address automatically. For this setting, a jumper on the Arduino adapter board need to be set shorting far side of header pins. 

#### (3) Plug-in AC adapters
The demo suite case has two AC adapters. Those need to be connected to 100V AC supply.  

#### (4) Start Wi-Fi access point
Turn-ON the left most switch on the USB hub. It start to provide power into Wi-Fi access point.  
Wait a while the access point is ready. When the access point bocome available, a center LED on the access point will be ON.  

![sw1](https://github.com/teddokano/mikan/blob/afe/remote_demo/references/pics/sw1.png)
![ap_led](https://github.com/teddokano/mikan/blob/afe/remote_demo/references/pics/ap_led.png)

#### (5) Turn-ON MCU board
Turn-ON second-left switch on the USB hub. 
MCU will start to work and show start message of "AFE demo / DHCP". When the system is ready, the LCD will show an IP address. 

![sw2](https://github.com/teddokano/mikan/blob/afe/remote_demo/references/pics/sw2.png)

#### (6) Conect iPad/Smartphone/PC to Wi-Fi
The Wi-Fi is available on access point. The SSID will be "NAFEdemo" and "NAFEdemo5G".  
"NAFEdemo" is using 2.4GHz and "NAFEdemo5G" is using 5GHz Wi-Fi. Both of them are same for accessing to the demo.  
Use password of "nafe2023" for both Wi-F network. 

#### (7) Access to IP address from browser
After Wi-Fi connection established, access to the demo can be done from an web-browser.  
The access should be done to the IP address on the small character LCD. 

#### (8) Click on NFAE13388 link
The browser shows available device list. Click on the NAFE13388 to show its demo page.  

## Procedure of turning-ON (Peer-to-peer LAN cable operation)
#### (1) Secure connections of boards and cables
After open the box, please make sure the boards and cables securely connected.  
The boards of AFE, adapter and MCU could be floating after porting. The connectors of DC input on AFE, USB and LAN-cable could be loose after transpotation.  

#### (2) Jumper setting for Fixed IP address
To perform peer-to-peer LAN cable communication, both of the MCU board and remote-device need to have fixed IP address. 
For this setting, a jumper on the Arduino adapter board need to be set shorting far side of header pins. 

#### (3) Conect PC (or remote device) with LAN cable
Connect LAN cable between MCU board and remote-device(PC).  
Configure the remote-device (PC) to have IP address of 
	IP address: 10.0.0.1
	Subnet mask: 255.255.255.0
	Router: 10.0.0.1

#### (4) Plug-in AC adapters
The demo suite case has two AC adapters. Those need to be connected to 100V AC supply.  

#### (5) Turn-ON MCU board
Turn-ON second-left switch on the USB hub. 
MCU will start to work and show start message of "AFE demo / FixedIP". When the system is ready, the LCD will show an IP address as "10.0.0.99". 

#### (6) Access to "10.0.0.99" from browser
The access should be done to "10.0.0.99" which can be found on the small character LCD. 

#### (7) Click on NFAE13388 link
The browser shows available device list. Click on the NAFE13388 to show its demo page.  
 
# Demo operation
## Basic operation
On the NAFE13388 demo page, it shows thermo-couple and load-cell measured values are presented in meters and plots.  
Pinch the thermo-couple tip with fingers and see change of temperature. Since it is body surface temperature on fingers, it may not be close to 36℃ but chenge of temperature can be observed.  
The thermo-couple reference junction temperature can be selected from 3 options: (1) Constant value, (2) Read value from temperature sensor located on the Arduino-adapter board and (3) NAFE13388's intenal temp sensor read value.  
Those option setting will be explained in next "Settings" section. 

The weight measurement can be done on the load-cell. The max load is 2kg.  
Put something on load-cell stage to see the value change. 
The weight measurement calibration can be performed. The calibration will be explained in next "Settings" section. 

## Settings
The measurement of the thermo-couple and the load-cell are done by voltage on channel 0 and 1.  
The measured voltages are converted by calculation in software using an offset cancelling and coefficient values.  

To show "Settings" panel, click on "show" button on "Settings:" section on the demo page.  
It will show "AFE measurement settings:" table.  
The table has two sections of "Ch0: Thermocouple" and "Ch1: Load-cell".  

Those settings are stored on MCU board strage. The setting will be reloaded into system at demo start (after system reset).  

### Ch0: Thermocouple
#### Coefficient and offset
For the thermo-couple, the demo expecting to use K-type thermo couple. It is having 40μV/℃ coefficient (default value).  
The offset voltage can be set in micro-volt. Those coefficient and offset values can be set manually.  

#### Reference junction temperature selection
The reference junction temperature is an absolute temperature reference for the thermo couple. The measured temperature is a delta between measureing tip and reference point.  
To convert the voltage to temperature, need to have a reference.  
This demo can choose reference temperature form 3 types.  
- "Constant:" = Constant value
- "External sensor" = Read value from temperature sensor (P3T1755) on Arduino-adapter board
- "Internal sensor" = NAFE13388's intenal temp sensor read value
The constant gives most stable velue for the demo because the temperature value is just converted from voltage.  
Other two options can be used for demo in temperature changing environment.  It is recommended to choose "External sensor" for demo because the P3T1755 has ±0.5℃ accuracy. This is better than the internal sensor accuracy (±3℃)
On bottom area of the 

For the external sensor, the I²C target address can be set. In current demo, the address is set 0x90 (in 8 bit representation). User don't need to edit this value unless hardware changed.  

#### Sensor read values
The bottom area of "Ch0: Thermocouple" section will show read temperature values from external and internal sensors.  
Those values will be kept refreshing while network commmunication is healthy.  

### Ch1: Load-cell
Load-cell measurement calibration can be done in two steps.  
- Unload the load-cell and press "Zero setting" button
- Put known weight objet on the load-cell stage. Put the weight in Calibration field then press "Scale calibration" button.  

## Limitations
### Simultaneous access from multiple remote device
The demo is designed for single client access. There is no control for bandwidth allocation of exclusive control on server code.  
The demo itself can serve the data to multiple remote devices but it may introduce poor server response.  
To have ideal performance, use only one remote device for accessing demo.  

### Multiple target device access
On device list page, it shows 3 target devices those can be demonstrated.  
The list shows NAFE13388, FXOS8700 and P3T1755. Click on those links, the device demo page will appear.  
Those device demo work as well. The FXOS8700 is a 6-axis accelerometer + magnetometer sensor on MCU board. The demo page will show it performance by tilting the board.  
P3T1755 is a temperature sensor on Arduino-adapter board. It is used for getting reference temperature for thermocouple demo but a stand-alone demo is possible with a page from this link.  
The temperature sensor demo page is reused from PCT2075. So it is not optimized for P3T1755. Some feature is not implemented.  
To avoid unneccesary device interaction and communication, close pages which is not demonstrated.  

## Tips
### Reload
On the web-browser, page reload may help to reset the page view and network comminication. 
The page reloading can be used when data update is not being done smoothly.  
However, the page reloading may not help if the problem is on MCU side. In that case, reboot the system to start demo freshly. 

# Trouble shooting
## Normal operation
The small character LCD shows system internal status.  
When the system in boot process, it shows "AFE demo / DHCP" or "AFE demo / Fixed IP". An IP-address will appear the boot process finished and system is ready.  

## Error on LCD
### LAN cable connection 
The LCD will show "No LAN / cable?" when the LAN cannot be started. In this case, check ethernet connection between MCU board and Wi-Fi access point (or PC).  

### DHCP fail
The LCD shows "DHCP / fail :(" when it cannot get IP address from DHCP server (Wi-Fi access point). This error can happen the MCU board turned-ON too fast.  
To fix this, confirm the Wi-Fi indicator LED (center LED) is ON then turn-ON MCU supply.  

# References
- NAFE13388
- MIMXRT1050-EVKB
- MicroPython
- mikan

# Appendix
## How to set fixed-IP on a PC (for Peer-to-peer LAN cable operation)
On Windows10, click "Start" menu and follow steps below.  

![fixed_IP_setup_0](https://github.com/teddokano/mikan/blob/afe/remote_demo/references/pics/fixed_IP_setup_0.png)  
![fixed_IP_setup_1](https://github.com/teddokano/mikan/blob/afe/remote_demo/references/pics/fixed_IP_setup_1.png)  
![fixed_IP_setup_2](https://github.com/teddokano/mikan/blob/afe/remote_demo/references/pics/fixed_IP_setup_2.png)  
