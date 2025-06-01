#!/usr/bin/python3
# Modified 17-Feb-2024
# tng@chegwin.org
# Retrieve: 
# 1: current temperature from a BMX2XX sensor
# 2: Send to redis


try:
    import sys,time
    from bmp280 import BMP280
    from smbus2 import SMBus
    import datetime
    from time import sleep
    import re
    import redis
    import configparser
    floattemp = 0
except ImportError:
    print ("ImportError")
    from smbus import SMBus

parser = configparser.ConfigParser()
parser.read('/etc/pithermostat.conf')

redishost=parser.get('redis','broker')
redisport=int(parser.get('redis','port'))
redisdb=parser.get('redis','db')
redistimeout=float(parser.get('redis','timeout'))
redthis=redis.StrictRedis(host=redishost,port=redisport, db=redisdb, socket_timeout=redistimeout)
# Find location from pithermostat.conf
room_location=parser.get('locale','location')
# Will generally be inside/outside
zone_location=parser.get('locale','zone')


time_to_live = 3600
###### IMPORTANT #############
###### How close to comfortable temperature is this sensor
###### determines how much weighting this sensor
###### if used at an extreme point in the house (say cellar), set to 1
###### if used centrally (living room), set to 3 or 4
# Now set in /etc/pithermostat.conf
zone_multiplier=parser.get('locale','multiplier')

sensor_name="temperature/"+room_location+"/sensor"
pressure_name="pressure/"+room_location+"/sensor"
mult_name="temperature/"+room_location+"/multiplier"
zone_name="temperature/"+room_location+"/zone"
print ("Sensor name is %s" % sensor_name)
print ("Multiplier name is %s" % mult_name)
print ("Zone name is %s" % zone_name)

def read_temp():
  try:
    # Initialise the BMP280
    bus = SMBus(1)
    bmp280 = BMP280(i2c_dev=bus)
    temperature = bmp280.get_temperature()
    pressure = bmp280.get_pressure()
    print('{:05.2f}*C {:05.2f}hPa'.format(temperature, pressure))
  except:
    print ("Failed to read temperature")
    temperature=14.7
    pressure=1000
  return temperature,pressure


while True:
  try: 
        (mytemp,mypressure) = read_temp()
        floattemp = float(mytemp)
        floatpressure = float(mypressure)
        #print ("Float temp = %f" % floattemp)
        redthis.set(sensor_name,floattemp)
        redthis.set(pressure_name,floatpressure)
        redthis.set(mult_name,zone_multiplier)
        redthis.set(zone_name,zone_location)
        redthis.expire(sensor_name,time_to_live)
        redthis.expire(pressure_name,time_to_live)
        redthis.expire(mult_name,time_to_live)
        redthis.expire(zone_name,time_to_live)
  except:
     print ("Unable to retrieve temperature")
  time.sleep(120)
