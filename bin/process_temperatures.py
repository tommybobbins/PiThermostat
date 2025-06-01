#!/usr/bin/python3
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
import configparser
import datetime
from time import sleep
import redis
#from google_calendar import google_calendar
from heating_water_cal import parse_calendar
from relay_state import get_relay, send_relay
from calculate_temps import calculate_temps,calculate_weighted_mean
import re
import sys
sys.path.append('/usr/local/python/lib')
from pithermostat.logging_helper import debug_log, info_log, error_log, warning_log

parser = configparser.ConfigParser()
parser.read('/etc/pithermostat.conf')

debug=parser.get('main','debug') # As string
Debug = {'True': True, 'False': False}.get(debug, False) # As Boolean
print ("Debug = %s\n" % Debug)
redishost=parser.get('redis','broker')
redisport=int(parser.get('redis','port'))
redisdb=parser.get('redis','db')
redistimeout=float(parser.get('redis','timeout'))
boiler_relay=parser.get('relays','boiler')
water_relay=parser.get('relays','water')
rotation_time=int(parser.get('main','rotation_time'))

redthis=redis.StrictRedis(host=redishost,port=redisport, db=redisdb, socket_timeout=redistimeout)
hysteresis_temp=float(parser.get('main','hysteresis_temp'))
summer_temp=float(parser.get('weather','summer_temp'))
summer_offset=float(parser.get('weather','summer_offset'))
#print ("Summer temp = %f" % summer_temp)
temp={}
multiplier={}
external_temp={}
external_multiplier={}

def update_relayinfo():
   boiler_state="error"
   water_state="error"
   try:
       boiler_state=str(get_relay("boiler"))
       water_state=str(get_relay("water"))
   except:
       debug_log("Unable to get relay state")
   try:
       redthis.set("relay/boiler", boiler_state)
       redthis.expire("relay/boiler", rotation_time)
       redthis.set("relay/water", water_state)
       redthis.expire("relay/water", rotation_time)
   except:
       debug_log("Unable to set redis relay state")
       print ("Unable to set redis relay state")

def send_call_boiler(on_or_off):
    debug_log("On/Off = %s " % on_or_off)
    if (on_or_off == "on"):
        try:
            redthis.set("boiler/req", "On")
            redthis.expire("boiler/req", rotation_time)
            redthis.set("boiler/4hourtimeout", "On")
            redthis.expire("boiler/4hourtimeout", 14400)
            #redthis.rpush("cellar/jobqueue", "/usr/local/bin/drayton on")
            send_relay("boiler","on")
        except:
            print ("Unable to update redis")
            debug_log("Unable to update redis")
    elif (on_or_off == "off"):
        try:
            redthis.set("boiler/req", "Off")
            redthis.expire("boiler/req", rotation_time)
            #redthis.rpush("cellar/jobqueue", "/usr/local/bin/drayton off")
            send_relay("boiler","off")
        except:
            print ("Unable to update redis")
            debug_log("Unable to update redis")
    else:
        print ("Need to send on or off to send_call_boiler()")

def send_call_water():
        water_req="Lost"
        water_state="Lost"
        expiry_time=rotation_time/10
        water_cal=0
        try:
          expiry_time=int(redthis.ttl("water/req"))
          if redthis.get("water/req"):
             water_req=str(redthis.get("water/req").decode("utf-8"))
          else:
             water_req=str(redthis.get("water/req"))
          water_cal=parse_calendar(2).lower()
          redthis.set("water/calendar", water_cal)
        except:
          redthis.set("water/calendar", water_state)
          debug_log("Expiry time of %s is %i . Calendar is %s" % (water_req,expiry_time,water_cal))
          debug_log("Lost one of %i, %s %s" % (expiry_time, water_req, water_cal))
          water_cal="true"
        if ( expiry_time <= 60 ):
             # Water has not been manually boosted and we set to calendar
           try:
              debug_log("Water temp = %s" % water_state)
              redthis.set("water/req", water_cal)
              redthis.expire("water/req", rotation_time)
              send_relay("water",water_cal)
           except: 
              water_state="Lost"
              debug_log("Expiry time of %s is %i . Calendar is %s" % (water_req,expiry_time,water_state))
              debug_log("Something went wrong")
              redthis.set("water/req", water_cal)
              redthis.expire("water/req", rotation_time)
        elif ( expiry_time <= rotation_time ):
              debug_log("Water state = %s %i" % (water_cal,expiry_time))
        else:
           # We are boosted
           debug_log("Nothing to do, water is boosted = %s %i" % (water_req,expiry_time))
           send_relay("water",water_req)


def read_temps():
    try:
        # First of all we grab google/Django happenings calendar. 
        # If the internet is down 
        # we set the value to 6.999
#        calendar_temp=float(google_calendar())
        calendar_temp=float(parse_calendar(1))
    except:
        debug_log("Google down or Django schedule not happening")
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
        calendar_temp += -summer_offset
        debug_log("Calendar temp = %f" % calendar_temp)
        debug_log("Outside Rolling mean temp = %f" % outside_rolling_mean)
        debug_log("Summer temp = %f" % summer_temp)
#    else:
#        print ("It is not summer")
    redthis.set("temperature/calendar", calendar_temp)
    debug_log("Found weather %f" % weather_temp)
    debug_log("Found user requested %f" % userreq_temp)
    debug_log("Found calendar %f" % calendar_temp)
    debug_log("Time until boiler needs poking = %i" % time_to_live)
    debug_log("Previous calendar = %f" % previous_calendar_temp)
    debug_log("Calendar_temp = %f" % calendar_temp)
    if (previous_calendar_temp != calendar_temp):
        #Calendar appointment has changed. Reset User Requested temperature 
        userreq_temp=calendar_temp 
        debug_log("Previous, current_calendar %f %f " % (previous_calendar_temp, calendar_temp))
        debug_log("User Requested is not equal to calendar %f %f " % (userreq_temp, calendar_temp))
        try:
            redthis.set("temperature/userrequested", userreq_temp)
        except:
            print ("Unable to update redis")
    debug_log("User Requested is now %f" % userreq_temp)
    redthis.set("temperature/inside/weightedmean", mean_temp)
    redthis.set("temperature/outside/weightedmean", mean_external_temp)
    debug_log("Mean temperature = %f" % mean_temp)

#   If in holiday mode, then keep userreq_temp at holiday_countdown
    try:
        userreq_temp = float(redthis.get("holiday_countdown"))
        debug_log("Holiday mode: User Requested Temp = %f" % userreq_temp)
    except:
        debug_log("Not in holiday Mode")

    if (time_to_live <= (int(rotation_time / 9))): 
        debug_log("Time to live is <= 35 seconds")
        debug_log("Time to live is %i" % (int(rotation_time/9)))
        working_temp = userreq_temp + hysteresis_temp
        # e.g. 21.3 = 20.0 + 1.3
        if (mean_temp <= userreq_temp):
#            e.g. Temp is 16.0
            send_call_boiler("on")
            debug_log("Switching On")
        elif (mean_temp >= working_temp):
#            e.g. Temp is 21.3
            send_call_boiler("off")
            debug_log("Switching Off")
        elif ((mean_temp <= working_temp) and (mean_temp >= userreq_temp)):
#            e.g. Temp is 20.6
            send_call_boiler("on")
            debug_log("Switching On")
        else:
             print ("Something gone wrong")
             debug_log("Switching Wrong")
    else:
        sleep(int(rotation_time/10))
        debug_log("Sleeping %i" % (rotation_time/10))
        #We are in the loop but can sleep until ttl<35

def process_temperatures():
    try:
        debug_log("Processing temperatures")
        #Sleep on startup as redis needs to be online first
        sleep(10)
        while True:
            debug_log("Looping")
            read_temps() 
            update_relayinfo()
            send_call_water()
            sleep(1)
    except Exception as e:
        error_log(f"Error in process_temperatures: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        process_temperatures()
    except Exception as e:
        error_log(f"Fatal error: {str(e)}")
        sys.exit(1)
   
