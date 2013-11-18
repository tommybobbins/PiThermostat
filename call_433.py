#!/usr/bin/python
import redis
import urllib2
#import expiry_time

redthis = redis.StrictRedis(host='433board',port=6379, db=0)

#If expiry_time doesn't exist, then we should add the expiry time
#If expiry_time < 40 then we should do it
#If expiry_time > 40 then we should wait


def call_url(on_or_off):
   try:
#       print ("Calling URL")
       response = urllib2.urlopen("http://433board/switchboiler/%s/" % on_or_off )
       redthis.set("boiler/req", "ok" )
       redthis.expire("boiler/req", 295) 
   except:
       print ("unable to open URL") 
     

def publish_redis(sensor_temp,calendar_temp,required_temp,delta_temp):
    redthis.set("temperature/sensor", "%f" % sensor_temp )
    redthis.set("temperature/calendar", "%f" % calendar_temp )
    redthis.set("temperature/required", "%f" % required_temp )
    redthis.set("temperature/boost", "%f" % delta_temp )



def send_boiler(boiler_state,timeout):
    if boiler_state: 
        switch_request="on"
    else:
        switch_request="off"
    timeout = int(timeout)
    expiry_time = (redthis.ttl("boiler/req"))
    expiry_time = int(expiry_time)
    if (expiry_time < 0 ):
        print ("We have no expiry time - setting one")
        redthis.set("boiler/req", "%s" % boiler_state)
        redthis.expire("boiler/req", "%i" % timeout )
    if (int(timeout) <= 40):
        #If requested a fast turnaround job, do it
        call_url(switch_request)
    elif (timeout > 40):
        #Requested to switch sometime, but not quickly
        if (expiry_time <= 40):
            call_url(switch_request)
        else:
#            print ("Not calling URL as we have a long expiry time")
            redthis.set("boiler/req", "%s" % boiler_state)
            redthis.expire("boiler/req", "%i" % expiry_time )
    else:
        print "Something wrong" 
