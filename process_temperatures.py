#!/usr/bin/python
# Modified 30-Oct-2013
# tng@chegwin.org
# Retrieve: 
# 1: target temperature from a calendar
# 2: current temperature from a TMP102 sensor
# 3: weather from the weather_file (or run weather_script and try again)
#    file is populated by weather-util. See retrieve-weather.sh for details

from sys import path
import datetime
from time import sleep
import redis
from google_calendar import google_calendar
import re
redthis = redis.StrictRedis(host='433board',port=6379, db=0, socket_timeout=3)
Debug=False

def read_temps():
    try:
        weather_temp=float(redthis.get("temperature/weather"))
        userreq_temp=float(redthis.get("temperature/userrequested"))
        ##### Optimal temp is the debug value we want to set the house to
        ##### if all else fails
        failover_temp=float(redthis.get("temperature/failover"))
        attic_temp=float(redthis.get("temperature/attic/sensor"))
        barab_temp=float(redthis.get("temperature/barab/sensor"))
        cellar_temp=float(redthis.get("temperature/cellar/sensor"))
        attic_mult=float(redthis.get("temperature/attic/multiplier"))
        barab_mult=float(redthis.get("temperature/barab/multiplier"))
        cellar_mult=float(redthis.get("temperature/cellar/multiplier"))
        previous_calendar_temp=float(redthis.get("temperature/calendar"))
        time_to_live=int(redthis.ttl("boiler/req"))
        calendar_temp=float(google_calendar())
        redthis.set("temperature/calendar", calendar_temp)
        
    except:
        print ("Unable to find redis stats or google not contactable.")
        weather_temp=0.6
        userreq_temp=6.6
        attic_temp=15.6
        barab_temp=15.6
        cellar_temp=15.6
        attic_mult=1
        barab_mult=1
        cellar_mult=1
        calendar_temp=16.6
        time_to_live=290
        previous_calendar_temp=calendar_temp
    if Debug: 
        print ("Found weather %f" % weather_temp)
        print ("Found user requested %f" % userreq_temp)
        print ("Found Barab %f" % barab_temp)
        print ("Found Cellar %f" % cellar_temp)
        print ("Found Attic %f" % attic_temp)
        print ("Found calendar %f" % calendar_temp)
        print ("Time until boiler needs poking = %i" % time_to_live)
    if (previous_calendar_temp != calendar_temp):
        #Calendar appointment has changed. Reset User Requested temperature 
        userreq_temp=calendar_temp 
        try:
            redthis.set("temperature/userrequested", userreq_temp)
        except:
            print ("Unable to update redis")
    if Debug:
        print ("User Requested is now %f" % userreq_temp)
    mean_temp = float((cellar_temp*cellar_mult) + (barab_temp*barab_mult) + (attic_temp*attic_mult))/(cellar_mult + barab_mult + attic_mult)
    if Debug:
        print ("Mean temperature = %f" % mean_temp)


    if (time_to_live <= 35): 
        if (mean_temp <= userreq_temp):
#            print ("Need to switch on boiler")
            try:
                redthis.set("boiler/req", "True")
                redthis.expire("boiler/req", 300)
                redthis.rpush("cellar/jobqueue", "/usr/local/bin/drayton on")
            except:
                print ("Unable to update redis") 
        elif (mean_temp >= userreq_temp):
#            print ("No need to switch on boiler")
            try:
                redthis.set("boiler/req", "False")
                redthis.expire("boiler/req", 300)
                redthis.rpush("cellar/jobqueue", "/usr/local/bin/drayton off")
            except:
                print ("Unable to update redis") 
        else:
             print ("Something gone wrong")

if __name__ == "__main__":
   while True:
       read_temps() 
       sleep(30)
   
