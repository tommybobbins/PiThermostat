PiThermostat
============

Raspberry Pi using a HY28 LCD touchscreen and a TMP102 to make an MQTT/thermostat display.

Uses pygame to build SDL interface to the thermometer
Uses weather-util to retrieve weather info:

sudo apt-get install weather-util

Edit retreive_weather.sh (it is currently set to Leeds/Bradford airport):

sudo cp retrieve_weather.sh /usr/local/bin/
sudo chmod a+x /usr/local/bin/retrieve_weather.sh

crontab -e
Add a line similar to the following to retrieve the weather for your location
13 0,6,12,18 * * * /usr/local/bin/retrieve_weather.sh

Copy the init script to /etc/init.d/temp.sh
insserv temp.sh

/etc/modules should look something like:
# /etc/modules: kernel modules to load at boot time.
#
# This file contains the names of kernel modules that should be loaded
# at boot time, one per line. Lines beginning with "#" are ignored.
# Parameters can be specified after the module name.

snd-bcm2835
fbtft dma
fbtft_device name=hy28a rotate=0 speed=48000000 fps=50
ads7846_device pressure_max=255 y_min=190 y_max=3850 gpio_pendown=17 x_max=3850 
x_min=230 x_plate_ohms=100 swap_xy=0 verbose=3

/boot/cmdline.txt should look something like:
dwc_otg.lpm_enable=0 console=ttyAMA0,115200 kgdboc=ttyAMA0,115200 console=tty1 r
oot=/dev/mmcblk0p2 rootfstype=ext4 elevator=deadline rootwait fbcon=map:10 fbcon
=font:VGA8x8
