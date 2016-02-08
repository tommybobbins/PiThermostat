#!/usr/bin/python
# Modified 19-Feb-2014
# tng@chegwin.org
# Plan B in case thermostat dies. Switch on heating for 2 hours per day
# if Redis queue down or thermostat is dead

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

import logging, datetime
dt = datetime.datetime.now()

logging.basicConfig(filename='/home/pi/TEMPERATURES/temps_%i_%i_%i.log' %(dt.year, dt.month, dt.day),level=logging.INFO)

logging_string=""
try:
    outside_temp=float(redthis.get("temperature/weather"))
    required_temp=float(redthis.get("temperature/userrequested"))
    boiler_req=(redthis.get("boiler/req"))
    logging_string += ("%f" % outside_temp)
    logging_string += ("\t%f" % required_temp)
    regex_temp = re.compile(r'^temperature\/(.*)\/sensor$')
    # Find all the keys matching temperature/*/sensor
    # For each key find, the sensor value
    all_tempkeys=(redthis.keys(pattern="temperature/*/sensor"))
    for tempkey in sorted(all_tempkeys):
        try:
            match = regex_temp.search(tempkey)
            location=match.group(1)
#            print ("location = %s " % location)
            value=float(redthis.get(tempkey))
            logging_string += ("\t%f" % value)
            print logging_string
        except:
            print ("Something went wrong!")
    logging_string += ("\t %s" % boiler_req)
except:
    outside_temp = 0
    sensor_temp = 0
    required_temp = 0
logging.info ("%s\n" % (logging_string ))
