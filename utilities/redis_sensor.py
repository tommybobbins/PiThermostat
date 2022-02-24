#!/usr/bin/python3
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
import smbus
import configparser
floattemp = 0

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
mult_name="temperature/"+room_location+"/multiplier"
zone_name="temperature/"+room_location+"/zone"
#print ("Sensor name is %s" % sensor_name)
#print ("Multiplier name is %s" % mult_name)
#print ("Zone name is %s" % zone_name)

def read_temp(i2c_address=0x48):

  i2c_ch = 1
  # TMP102 address on the I2C bus
  i2c_address = 0x48
  # Register addresses
  reg_temp = 0x00
  reg_config = 0x01
  # Calculate the 2's complement of a number
  def twos_comp(val, bits):
    if (val & (1 << (bits - 1))) != 0:
      val = val - (1 << bits)
    return val

  # Read temperature registers and calculate Celsius
  def read_temp():
    # Read temperature registers
    val = bus.read_i2c_block_data(i2c_address, reg_temp, 2)
    temp_c = (val[0] << 4) | (val[1] >> 5)
    # Convert to 2s complement (temperatures can be negative)
    temp_c = twos_comp(temp_c, 12)
    # Convert registers value to temperature (C)
    temp_c = temp_c * 0.0625
    return temp_c

  # Initialize I2C (SMBus)
  bus = smbus.SMBus(i2c_ch)
  # Read the CONFIG register (2 bytes)
  val = bus.read_i2c_block_data(i2c_address, reg_config, 2)
  # Set to 4 Hz sampling (CR1, CR0 = 0b10)
  val[1] = val[1] & 0b00111111
  val[1] = val[1] | (0b10 << 6)
  # Write 4 Hz sampling back to CONFIG
  bus.write_i2c_block_data(i2c_address, reg_config, val)
  # Read CONFIG to verify that we changed it
  val = bus.read_i2c_block_data(i2c_address, reg_config, 2)

  temperature = read_temp()
  #print(round(temperature, 2), "C")
  return(temperature)


while True:
    try: 
        mytemp = read_temp(i2c_address=0x48)
        floattemp = float(mytemp)
        #print ("Float temp = %f" % floattemp)
        redthis.set(sensor_name,floattemp)
        redthis.set(mult_name,zone_multiplier)
        redthis.set(zone_name,zone_location)
        redthis.expire(sensor_name,time_to_live)
        redthis.expire(mult_name,time_to_live)
        redthis.expire(zone_name,time_to_live)
    except:
        print ("Unable to retrieve temperature")
    time.sleep(120)
