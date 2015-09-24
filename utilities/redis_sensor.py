#!/usr/bin/python
# Modified 30-Oct-2013
# tng@chegwin.org
# Retrieve: 
# 1: current temperature from a TMP102 sensor
# 2: Send to redis

import sys,time
from sys import path
import datetime
from time import sleep
import re
import redis
from ConfigParser import SafeConfigParser

parser = SafeConfigParser()
parser.read('/etc/pithermostat.conf')

redishost=parser.get('redis','broker')
redisport=int(parser.get('redis','port'))
redisdb=parser.get('redis','db')
redistimeout=float(parser.get('redis','timeout'))
redthis=redis.StrictRedis(host=redishost,port=redisport, db=redisdb, socket_timeout=redistimeout)


time_to_live = 3600
###### IMPORTANT #############
###### How close to comfortable temperature is this sensor
###### determines how much weighting this sensor
###### if used at an extreme point in the house (say cellar), set to 1
###### if used centrally (living room), set to 3 or 4
multiplier = 3
#import crankers
sys.path.append("/usr/local/lib/python2.7/site-packages/Adafruit-Raspberry-Pi-Python-Code/Adafruit_I2C/")
from Adafruit_I2C import Adafruit_I2C
room_location="barab"
sensor_name="temperature/"+room_location+"/sensor"
mult_name="temperature/"+room_location+"/multiplier"
#print ("Sensor name is %s" % sensor_name)
#print ("Multiplier name is %s" % mult_name)

class Tmp102:
  i2c = None

  # Constructor
  def __init__(self, address=0x48, mode=1, debug=False):
    self.i2c = Adafruit_I2C(address, debug=debug)

    self.address = address
    self.debug = debug
    # Make sure the specified mode is in the appropriate range
    if ((mode < 0) | (mode > 3)):
      if (self.debug):
        print "Invalid Mode: Using STANDARD by default"
      self.mode = self.__BMP085_STANDARD
    else:
      self.mode = mode

  def readTemperature(self):
    "Gets the compensated temperature in degrees celcius"
    self.i2c.write8(0, 0x00)                 # Set temp reading mode
    raw = self.i2c.readList(0,2)
    if (self.debug):
        print ("Raw0 = %s, Raw1 = %s" % (raw[0],raw[1]))
    negative = (raw[0] >> 7) == 1
    shift = 4
    if not negative:
        val = (((raw[0] * 256) + raw[1]) >> shift) * 0.0625
    else:
        remove_bit = 0b011111111111
        ti = (((raw[0] * 256) + raw[1]) >> shift)
        # Complement, but remove the first bit.
        ti = float(~ti & remove_bit)
        val = float(float(-(ti))*0.0625)
    if (self.debug):
        print val
    return val

while True:
    try: 
        mytemp = Tmp102(address=0x48)
        floattemp = mytemp.readTemperature()
#        print ("Float temp = %f" % floattemp)
        redthis.set(sensor_name,floattemp)
        redthis.set(mult_name,multiplier)
        redthis.expire(sensor_name,time_to_live)
        redthis.expire(mult_name,time_to_live)
    except:
        print ("Unable to retrieve temperature")
    time.sleep(120)
      
