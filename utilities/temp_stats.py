#!/usr/bin/python
# Modified 19-Feb-2014
# tng@chegwin.org
# Plan B in case thermostat dies. Switch on heating for 2 hours per day
# if Redis queue down or thermostat is dead

from time import sleep
import redis
from ConfigParser import SafeConfigParser

parser = SafeConfigParser()
parser.read('/etc/pithermostat.conf')

redishost=parser.get('redis','broker')
redisport=int(parser.get('redis','port'))
redisdb=parser.get('redis','db')
redistimeout=float(parser.get('redis','timeout'))
redthis=redis.StrictRedis(host=redishost,port=redisport, db=redisdb, socket_timeout=redistimeout)

import logging, datetime
dt = datetime.datetime.now()

logging.basicConfig(filename='/home/pi/TEMPERATURES/temps_%i_%i_%i.log' %(dt.year, dt.month, dt.day),level=logging.INFO)

try:
    outside_temp=float(redthis.get("temperature/weather"))
    barab_sensor_temp=float(redthis.get("temperature/barab/sensor"))
    attic_sensor_temp=float(redthis.get("temperature/attic/sensor"))
    cellar_sensor_temp=float(redthis.get("temperature/cellar/sensor"))
    required_temp=float(redthis.get("temperature/userrequested"))
    damocles_sensor_temp=(0.0)
    eden_sensor_temp=float(redthis.get("temperature/eden/sensor"))
    forno_sensor_temp=float(redthis.get("temperature/forno/sensor"))
except:
    outside_temp = 0
    sensor_temp = 0
    required_temp = 0
logging.info ("%s\t%f\t%f\t%f\t%f\t%f\t%f\t%f\t%f" % (dt,outside_temp,barab_sensor_temp,required_temp, attic_sensor_temp, cellar_sensor_temp, damocles_sensor_temp, eden_sensor_temp, forno_sensor_temp ))
