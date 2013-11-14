#!/usr/bin/python
import redis
import urllib2

redthis = redis.StrictRedis(host='433board',port=6379, db=0)
#response = urllib2.urlopen('http://433board/switchboiler/on/')
#response = urllib2.urlopen('http://433board/switchboiler/on/')
def publish_redis(sensor,weather,target,req):
    redthis.set("temperature/sensor", "%f" % sensor )
    redthis.set("temperature/weather", "%f" % weather )
    redthis.set("temperature/target", "%f" % target )
    redthis.set("boiler/req", "%s" % req )
    redthis.expire("boiler/req", "%i" % 240 )

def send_boiler(boiler_state):
    if boiler_state: 
        try:
#            print ("Boiler state is true. Switching on")
            response = urllib2.urlopen('http://433board/switchboiler/on/')
        except:
            print ("unable to open URL") 
    else:
        try:
#            print ("Boiler state is False. Switching off")
            response = urllib2.urlopen('http://433board/switchboiler/off/')
        except:
            print ("unable to open URL") 
