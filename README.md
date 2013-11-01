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
