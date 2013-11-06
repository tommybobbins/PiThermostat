#!/usr/bin/python
# Modified 30-Oct-2013
# tng@chegwin.org
# Retrieve: 
# 1: target temperature from a calendar
# 2: current temperature from a TMP102 sensor
# 3: weather from the weather_file (or run weather_script and try again)
#    file is populated by weather-util. See retrieve-weather.sh for details

import sys, os, time
import threading
import datetime
from time import sleep
import fileinput
from processcalendar import parse_calendar
import re
sys.path.append('/usr/local/lib/python2.7/site-packages/Adafruit-Raspberry-Pi-Python-Code/Adafruit_CharLCDPlate')
from Adafruit_I2C import Adafruit_I2C

# Set this to something sensible in case we have no calendar

#print parse_calendar()

try:
    target_temp=parse_calendar()
except:
    target_temp=14

outside_temp="unknown"
weather_file='/tmp/weather_conditions.txt'
weather_script='/usr/local/bin/retrieve_weather.sh'
regex = re.compile(r'\s+Temperature:\s+(\d+) F \((\d+) C\)')

def parse_weather():
    for line in fileinput.input(weather_file):
        line = line.rstrip() 
        match = regex.search(line)
        if match:
            outside_temp= int(match.group(2))
            return(outside_temp)

#Check to see whether the weather has been downloaded.
try:
    weather_temp=parse_weather()
except IOError:
   from subprocess import call
   call([weather_script])	
   weather_temp=parse_weather()


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


def read_temps():
    mytemp = Tmp102(address=0x48)
    floattemp = mytemp.readTemperature()[1]
    weathernow = ("%i" % weather_temp)
    try:
        target_temp=parse_calendar()
    except:
        target_temp=14
#    print "target temp %i" % target_temp
    return (floattemp, target_temp, weather_temp)

