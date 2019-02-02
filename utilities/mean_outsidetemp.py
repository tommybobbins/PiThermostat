#!/usr/bin/python
### For a given temperature/external/mean, populate a rolling redis list temperature/external/rollingtemp
### with 48 entries on. Then calculate the mean and populate temperature/external/rollingmean
### Used to determine whether it is Summer or Winter
import redis
from time import sleep
from ConfigParser import SafeConfigParser
import random
numerator = 0


parser = SafeConfigParser()
parser.read('/etc/pithermostat.conf')

redishost=parser.get('redis','broker')
redisport=int(parser.get('redis','port'))
redisdb=parser.get('redis','db')
redistimeout=float(parser.get('redis','timeout'))
redthis=redis.StrictRedis(host=redishost,port=redisport, db=redisdb, socket_timeout=redistimeout)

try:
    current_eden_temp = float(redthis.get('temperature/outside/weightedmean'))
    #current_eden_temp = float(random.randrange(15.0,19.0,1)) # For testing
#    print ("Current eden temperature %f" % current_eden_temp)
    redthis.rpush("temperature/outside/rollingtemp", current_eden_temp) 
    length_of_list = int(redthis.llen('temperature/outside/rollingtemp'))
except:
    print ("Something went wrong with redis")
    exit(0)
if (length_of_list > 48):
    redthis.lpop("temperature/outside/rollingtemp")
else:
    print ("Length of list = %i" % length_of_list)
for listcounter in range(0,(length_of_list - 1)):
    temp = float(redthis.lindex('temperature/outside/rollingtemp', listcounter))
    numerator += temp
#    print ("temp = %f " % temp ) 
#print ("Numerator = %f " % numerator)
denominator = length_of_list - 1
mean_temp = numerator/denominator
redthis.set('temperature/outside/rollingmean', mean_temp)
#print ("Mean temp = %f " % mean_temp) 
