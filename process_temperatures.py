#!/usr/bin/python
# Modified 30-Oct-2013
# tng@chegwin.org
# Retrieve: 
# 1: target temperature from a calendar
# 2: current temperature from a TMP102 sensor
# 3: weather from the weather_file (or run weather_script and try again)
#    file is populated by weather-util. See retrieve-weather.sh for details
# Modified 24-June-2015
# tng@chegwin.org
# Move to django_happenings
# Modified 27-Sep-2015
# tng@chegwin.org/jon@rosslug.org.uk
# Modularised, added config file, made generic

from sys import path
from ConfigParser import SafeConfigParser
import datetime
from time import sleep
import redis
#from google_calendar import google_calendar
from django_happenings import parse_calendar
from calculate_temps import calculate_temps,calculate_weighted_mean
import re
parser = SafeConfigParser()
parser.read('/etc/pithermostat.conf')

debug=parser.get('main','debug') # As string
Debug = {'True': True, 'False': False}.get(debug, False) # As Boolean
print ("Debug = %s\n" % Debug)
redishost=parser.get('redis','broker')
redisport=int(parser.get('redis','port'))
redisdb=parser.get('redis','db')
redistimeout=float(parser.get('redis','timeout'))

redthis=redis.StrictRedis(host=redishost,port=redisport, db=redisdb, socket_timeout=redistimeout)
hysteresis_temp=0.5
summer_temp=float(parser.get('weather','summer_temp'))
#print ("Summer temp = %f" % summer_temp)
temp={}
multiplier={}
external_temp={}
external_multiplier={}

def send_call_boiler(on_or_off):
    if Debug:
        print ("On/Off = %s " % on_or_off)
    if (on_or_off == "on"):
        try:
            redthis.set("boiler/req", "True")
            redthis.expire("boiler/req", 300)
            redthis.set("boiler/4hourtimeout", "True")
            redthis.expire("boiler/4hourtimeout", 14400)
            redthis.rpush("cellar/jobqueue", "/usr/local/bin/drayton on")
        except:
            print ("Unable to update redis")
    elif (on_or_off == "off"):
        try:
            redthis.set("boiler/req", "False")
            redthis.expire("boiler/req", 300)
            redthis.rpush("cellar/jobqueue", "/usr/local/bin/drayton off")
        except:
            print ("Unable to update redis")
    else:
        print ("Need to send on or off to send_call_boiler()")


def read_temps():
    try:
        # First of all we grab google/Django happenings calendar. 
        # If the internet is down 
        # we set the value to 6.999
#        calendar_temp=float(google_calendar())
        calendar_temp=float(parse_calendar())
    except:
        print ("Google down or Django happenings not happening")
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
        (mean_temp, mean_external_temp) = calculate_temps()
    except:
        mean_temp=15.623
        mean_external_temp=10.123
    try:
        outside_rolling_mean=float(redthis.get("temperature/outside/rollingmean"))
    except:
        outside_rolling_mean = 6.33
    # Store our previous google calendar temperature for ref.
    previous_calendar_temp=float(redthis.get("temperature/calendar"))
    boiler_state=redthis.get("boiler/req")
    time_to_live=int(redthis.ttl("boiler/req"))
    # Store our google calendar temperature for future reference
    if (outside_rolling_mean >= summer_temp):
        calendar_temp += -4.0
        if Debug:
            print ("Calendar temp = %f" % calendar_temp)
            print ("Outside Rolling mean temp = %f" % outside_rolling_mean)
            print ("Summer temp = %f" % summer_temp)
#    else:
#        print ("It is not summer")
    redthis.set("temperature/calendar", calendar_temp)
    if Debug: 
        print ("Found weather %f" % weather_temp)
        print ("Found user requested %f" % userreq_temp)
        print ("Found calendar %f" % calendar_temp)
        print ("Time until boiler needs poking = %i" % time_to_live)
        print ("Previous calendar = %f" % previous_calendar_temp)
        print ("Calendar_temp = %f" % calendar_temp)
    if (previous_calendar_temp != calendar_temp):
        #Calendar appointment has changed. Reset User Requested temperature 
        userreq_temp=calendar_temp 
        if Debug:
            print ("Previous, current_calendar %f %f " % (previous_calendar_temp, calendar_temp))
            print ("User Requested is not equal to calendar %f %f " % (userreq_temp, calendar_temp))
        try:
            redthis.set("temperature/userrequested", userreq_temp)
        except:
            print ("Unable to update redis")
    if Debug:
        print ("User Requested is now %f" % userreq_temp)
    redthis.set("temperature/inside/weightedmean", mean_temp)
    redthis.set("temperature/outside/weightedmean", mean_external_temp)
    if Debug:
        print ("Mean temperature = %f" % mean_temp)

#   If in holiday mode, then keep userreq_temp at holiday_countdown
    try:
        userreq_temp = float(redthis.get("holiday_countdown"))
        if Debug:
            print ("Holiday mode: User Requested Temp = %f" % userreq_temp)
    except:
        if Debug:
            print ("Not in holiday Mode")

    if (time_to_live <= 35): 
        if Debug:
            print ("Time to live is <= 35 seconds")
        working_temp = userreq_temp + hysteresis_temp
        # e.g. 21.3 = 20.0 + 1.3
        if (mean_temp <= userreq_temp):
#            e.g. Temp is 16.0
            send_call_boiler("on")
            if Debug:
                print ("Switching On")
        elif (mean_temp >= working_temp):
#            e.g. Temp is 21.3
            send_call_boiler("off")
            if Debug:
                print ("Switching Off")
        elif ((mean_temp <= working_temp) and (mean_temp >= userreq_temp)):
#            e.g. Temp is 20.6
            send_call_boiler("on")
            if Debug:
                print ("Switching On")
        else:
             print ("Something gone wrong")
             if Debug:
                 print ("Switching Wrong")
    else:
        sleep(0)
        #We are in the loop but can sleep until ttl<35

if __name__ == "__main__":
   while True:
       read_temps() 
       sleep(30)
   
