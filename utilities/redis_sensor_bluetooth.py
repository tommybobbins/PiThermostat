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
sys.path.append("/usr/local/lib/python2.7/site-packages/Adafruit-Raspberry-Pi-Python-Code/Adafruit_I2C/")
from Adafruit_I2C import Adafruit_I2C
from ConfigParser import SafeConfigParser

parser = SafeConfigParser()
parser.read('/etc/pithermostat.conf')

redishost=parser.get('redis','broker')
redisport=int(parser.get('redis','port'))
redisdb=parser.get('redis','db')
redistimeout=float(parser.get('redis','timeout'))
redthis=redis.StrictRedis(host=redishost,port=redisport, db=redisdb, socket_timeout=redistimeout)

room_location="attic"
sensor_name="temperature/"+room_location+"/sensor"
print ("Sensor name is %s" % sensor_name)

class Tmp102:
  i2c = None

  # Constructor
  def __init__(self, address=0x48, mode=1, debug=True):
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

  def readRawTemp(self):
    "Reads the raw (uncompensated) temperature from the sensor"
    self.i2c.write8(0, 0x00)                 # Set temp reading mode
    raw = self.i2c.readList(0,2)

    val = raw[0] << 4;
    val |= raw[1] >> 4;

    return val


  def readTemperature(self):
    "Gets the compensated temperature in degrees celcius"

    RawBytes = self.readRawTemp()  #get the temp from readRawTemp (above)
    temp = float(float(RawBytes) * 0.0625)  #this is the conversion value from the data sheet.
    if (self.debug):
      print "DBG: Raw Temp: 0x%04X (%d)" % (RawBytes & 0xFFFF, RawBytes)
      print "DBG: Calibrated temperature = %f C" % temp
    
    return RawBytes,temp

while True:
    try: 
        mytemp = Tmp102(address=0x48)
        floattemp = mytemp.readTemperature()[1]
        print ("Float temp = %f" % floattemp)
        redthis.set(sensor_name,floattemp)
    except:
        print ("Unable to retrieve temperature")
    time.sleep(120)
      
