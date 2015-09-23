#!/usr/bin/python
import redis
import urllib2
from ConfigParser import SafeConfigParser
#import expiry_time

parser = SafeConfigParser()
parser.read('/etc/pithermostat.conf')

redishost=parser.get('redis','broker')
redisport=parser.get('redis','port')
redisdb=parser.get('redis','db')
redistimeout=float(parser.get('redis','timeout'))
redthis=redis.StrictRedis(host=redishost,port=redisport, db=redisdb, socket_timeout=redistimeout)

#If expiry_time doesn't exist, then we should add the expiry time
#If expiry_time < 40 then we should do it
#If expiry_time > 40 then we should wait


def call_url(on_or_off):
   try:
#       print ("Calling URL")
#       response = urllib2.urlopen("http://433board/switchboiler/%s/" % on_or_off )
       server_alive=redthis.get("temperature/weather")
       if server_alive:
           command_to_rethis = ("/usr/local/bin/drayton %s" % on_or_off)
           redthis.rpush("cellar/jobqueue", command_to_rethis)
           redthis.set("boiler/req", "ok" )
           redthis.expire("boiler/req", 295) 
   except:
       print ("unable to open URL") 
     

def publish_redis(sensor_temp,calendar_temp,required_temp):
    try:
        server_alive=redthis.get("temperature/weather")
        if server_alive:
#    print ("Sensor = %f, Calendar = %f, Required = %f\n" % (sensor_temp, calendar_temp,required_temp ))
#   From the temperature sensor
            redthis.set("temperature/barab/sensor", "%f" % sensor_temp )
#   From the Django calendar
            redthis.set("temperature/calendar", "%f" % calendar_temp )
#   From the required temp (working temp)
            redthis.set("temperature/required", "%f" % required_temp )
#   From the boosted (working_temp_addition)
    #        redthis.set("temperature/boosted", "%f" % delta_temp )
#   Turbo True/False (Enjiia button pressed)
#            redthis.set("temperature/turbo", "%s" % boosted )
    except:
        print "Unable to redis.set"



def send_boiler(boiler_state,timeout):
    try:
        if boiler_state: 
            switch_request="on"
        else:
            switch_request="off"
        timeout = int(timeout)
        expiry_time = (redthis.ttl("boiler/req"))
        expiry_time = int(expiry_time)
        if (expiry_time < 0 ):
#            print ("We have no expiry time - setting one")
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
    except:
           print "Unable to update redis"
