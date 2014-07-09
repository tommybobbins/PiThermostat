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
hysteresis_temp=0.5
Debug=False

def calculate_weighted_mean(incoming_multiplier,incoming_temp):
    numerator = 0
    denominator = 0
    running_mean = 14.666
    for item in incoming_multiplier.keys():
        try:
            numerator += incoming_multiplier[item]*incoming_temp[item] 
            denominator += incoming_multiplier[item] 
            running_mean =  float(numerator/denominator)
#            print ("Running mean %f " % running_mean)
        except:
            print ("Something went wrong\n")
            running_mean = 14.665
#        print ("numerator = %i" % numerator)
#        print ("denominator = %i" % denominator)
    return(running_mean) 


def read_temps():
    try:
        # First of all we grab google calendar. If the internet is down 
        # we set the value to 6.999
        calendar_temp=float(google_calendar())
    except:
        print ("Google down")
        calendar_temp=6.999
    try:
        #Read in all the previous settings
        weather_temp=float(redthis.get("temperature/weather"))
        userreq_temp=float(redthis.get("temperature/userrequested"))
        ##### Optimal temp is the debug value we want to set the house to
        ##### if all else fails
        failover_temp=float(redthis.get("temperature/failover"))
    except:
        print ("Unable to find redis stats")
        weather_temp=14.999
        userreq_temp=6.999
        time_to_live=290
        failover_temp = 14.663
        previous_calendar_temp=calendar_temp
    try:
        attic_temp=float(redthis.get("temperature/attic/sensor"))
        attic_mult=float(redthis.get("temperature/attic/multiplier"))
    except:
        attic_temp = 0
        attic_mult = 0
    try:
        barab_temp=float(redthis.get("temperature/barab/sensor"))
        barab_mult=float(redthis.get("temperature/barab/multiplier"))
    except:
        barab_temp = 0
        barab_mult = 0
    try:
        cellar_temp=float(redthis.get("temperature/cellar/sensor"))
        cellar_mult=float(redthis.get("temperature/cellar/multiplier"))
    except:
        cellar_temp = 0 
        cellar_mult = 0 
    # Store our previous google calendar temperature for ref.
    previous_calendar_temp=float(redthis.get("temperature/calendar"))
    boiler_state=redthis.get("boiler/req")
    time_to_live=int(redthis.ttl("boiler/req"))
    # Store our google calendar temperature for future reference
    redthis.set("temperature/calendar", calendar_temp)
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
    try:
        damo_temp=float(redthis.get("temperature/damocles/sensor"))
        damo_mult=float(redthis.get("temperature/damocles/multiplier"))
        multiplier = {'attic': attic_mult, 'barab': barab_mult, 'cellar': cellar_mult, 'damocles': damo_mult}
        temp = {'attic': attic_temp, 'barab': barab_temp, 'cellar': cellar_temp, 'damocles': damo_temp}
        mean_temp = calculate_weighted_mean(multiplier,temp)
    except:
        multiplier = {'attic': attic_mult, 'barab': barab_mult, 'cellar': cellar_mult}
        temp = {'attic': attic_temp, 'barab': barab_temp, 'cellar': cellar_temp}
        mean_temp = calculate_weighted_mean(multiplier,temp)
    redthis.set("temperature/weightedmean", mean_temp)
    if Debug:
        print ("Mean temperature = %f" % mean_temp)


    if (time_to_live <= 35): 
        working_temp = userreq_temp + hysteresis_temp
        # e.g. 21.3 = 20.0 + 1.3
        if (mean_temp <= userreq_temp):
#            e.g. Temp is 16.0
#            print ("Need to switch on boiler")
            try:
                redthis.set("boiler/req", "True")
                redthis.expire("boiler/req", 300)
                redthis.set("boiler/4hourtimeout", "True")
                redthis.expire("boiler/4hourtimeout", 14400)
                redthis.rpush("cellar/jobqueue", "/usr/local/bin/drayton on")
            except:
                print ("Unable to update redis") 
        elif (mean_temp >= working_temp):
#            e.g. Temp is 21.3
#            print ("No need to switch on boiler")
            try:
                redthis.set("boiler/req", "False")
                redthis.expire("boiler/req", 300)
                redthis.rpush("cellar/jobqueue", "/usr/local/bin/drayton off")
            except:
                print ("Unable to update redis") 
        elif ((mean_temp <= working_temp) and (mean_temp >= userreq_temp)):
#            e.g. Temp is 20.6
#            print ("Need to switch on boiler")
            try:
                redthis.set("boiler/req", "True")
                redthis.expire("boiler/req", 300)
                redthis.set("boiler/4hourtimeout", "True")
                redthis.expire("boiler/4hourtimeout", 14400)
                redthis.rpush("cellar/jobqueue", "/usr/local/bin/drayton on")
            except:
                print ("Unable to update redis") 
        else:
             print ("Something gone wrong")
    else:
        sleep(0)
        #We are in the loop but can sleep until ttl<35

if __name__ == "__main__":
   while True:
       read_temps() 
       sleep(30)
   
