#!/usr/bin/python
### For a given temperature/sensor/eden, populate a rolling redis list temperature/rollingtemp/eden
### with 24 entries on. Then calculate the mean and populate temperature/rollingmean/eden
### Used to determine whether it is Summer or Winter
import redis
from time import sleep
import random
numerator = 0
redthis = redis.StrictRedis(host='433host',port=6379, db=0,socket_timeout=3)
try:
    current_eden_temp = float(redthis.get('temperature/sensor/eden'))
    #current_eden_temp = float(random.randrange(15.0,19.0,1)) # For testing
#    print ("Current eden temperature %f" % current_eden_temp)
    redthis.rpush("temperature/rollingtemp/eden", current_eden_temp) 
    length_of_list = int(redthis.llen('temperature/rollingtemp/eden'))
except:
    print ("Something went wrong with redis")
    exit(0)
if (length_of_list > 24):
    redthis.lpop("temperature/rollingtemp/eden")
else:
    print ("Length of list = %i" % length_of_list)
for listcounter in range(0,(length_of_list - 1)):
    temp = float(redthis.lindex('temperature/rollingtemp/eden', listcounter))
    numerator += temp
    print ("temp = %f " % temp ) 
#print ("Numerator = %f " % numerator)
denominator = length_of_list
mean_temp = numerator/denominator
redthis.set('temperature/rollingmean/eden', mean_temp)
#print ("Mean temp = %f " % mean_temp) 
