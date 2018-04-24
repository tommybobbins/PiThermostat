#!/usr/bin/python
# Modified 30-Oct-2013
# tng@chegwin.org
# Retrieve: 
# 1: target temperature from a calendar
# 2: current temperature from a TMP102 sensor
# 3: weather from the weather_file (or run weather_script and try again)
#    file is populated by weather-util. See retrieve-weather.sh for details

import sys,time
from sys import path
import datetime
from time import sleep
import re
#sys.path.append("/usr/local/lib/python2.7/site-packages/Adafruit/I2C")
#sys.path.append("/usr/local/lib/python2.7/site-packages/Adafruit-Raspberry-Pi-Python-Code/Adafruit_I2C/")
#print sys.path
#/master/Adafruit_GPIO/I2C.py) in the Python GPIO library.  Import with `import Adafruit_GPIO.I2C as I2C` and create an instance of `I2C.Device` instead of the old `Adafruit_I2C` class
import Adafruit_GPIO.I2C as I2C
import logging, datetime
dt = datetime.datetime.now()
floattemp=0

logging.basicConfig(filename='/home/pi/temp_sensor.log',level=logging.INFO)

class Tmp102:
  i2c = None

  # Constructor
  def __init__(self, address=0x48, mode=1, debug=False):
    self.i2c = I2C.Device(address, busnum=1)

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
    "Reads the raw (uncompensated) temperature from the sensor"
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
        val = float(-(ti))*0.0625
    if (self.debug):
        print val
    return val



mytemp = Tmp102(address=0x48)
floattemp = float(mytemp.readTemperature())
print ("%s Float temp = %f" % (dt,floattemp))
logging.info("%s Float temp = %f" % (dt,floattemp))
