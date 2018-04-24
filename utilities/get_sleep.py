#!/usr/bin/python
import redis
import subprocess
from time import sleep
from ConfigParser import SafeConfigParser
parser = SafeConfigParser()
parser.read('/etc/pithermostat.conf')

redishost=parser.get('redis','broker')
redisport=int(parser.get('redis','port'))
redisdb=parser.get('redis','db')
redistimeout=float(parser.get('redis','timeout'))

redthis=redis.StrictRedis(host=redishost,port=redisport, db=redisdb, socket_timeout=redistimeout)
try: 
    redthis.set("boiler/4hourtimeout", "True")
    redthis.expire("boiler/4hourtimeout", 43200)
    print ("12 hours sleep enabled")
except:
    print ("Unable to write to redis")
