#!/usr/bin/python
# Modified 23-May-2016
# tng@chegwin.org
# Parse all voltages and store in /home/pi/LOGGING for later analysis

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

logging.basicConfig(filename='/home/pi/LOGGING/voltages_%i_%i_%i.log' %(dt.year, dt.month, dt.day),level=logging.INFO)

logging_string=""
try:
    logging_string += ("%s\t" % dt)
    regex_volt = re.compile(r'^voltage\/(.*)\/sensor$')
    # Find all the keys matching voltage/*/sensor
    # For each key find, the sensor value
    all_voltkeys=(redthis.keys(pattern="voltage/*/sensor"))
    for voltkey in sorted(all_voltkeys):
        try:
            match = regex_volt.search(voltkey)
            location=match.group(1)
#            print ("location = %s " % location)
            value=float(redthis.get(voltkey))
            logging_string += ("\t%f" % value)
#           print logging_string
        except:
            print ("Something went wrong!")
except:
    print ("Something went wrong!")
logging.info ("%s" % (logging_string ))
