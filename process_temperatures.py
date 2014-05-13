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


def read_temps():
    try:
        weather_temp=float(redthis.get("temperature/weather"))
        working_temp=float(redthis.get("temperature/required"))
        ##### Optimal temp is the debug value we want to set the house to
        ##### if all else fails
        optimal_temp=float(redthis.get("temperature/optimal"))
        barab_temp=float(redthis.get("temperature/barab/sensor"))
        cellar_temp=float(redthis.get("temperature/cellar/sensor"))
        attic_temp=float(redthis.get("temperature/attic/sensor"))
        barab_mult=float(redthis.get("temperature/barab/multiplier"))
        cellar_mult=float(redthis.get("temperature/cellar/multiplier"))
        attic_mult=float(redthis.get("temperature/attic/multiplier"))
        target_temp=float(google_calendar())
    except:
        print ("Unable to find redis stats or google not contactable.")
        weather_temp=0.6
        optimal_temp=6.6
        working_temp=optimal_temp
        barab_temp=15.6
        cellar_temp=15.6
        attic_temp=15.6
        calendar_temp=16.6
    print ("Found weather %f" % weather_temp)
    print ("Found working %f" % working_temp)
    print ("Found optimal %f" % optimal_temp)
    print ("Found Barab %f" % barab_temp)
    print ("Found Cellar %f" % cellar_temp)
    print ("Found Attic %f" % attic_temp)
    print ("Found calendar %f" % target_temp)
    mean_temp = float((cellar_temp*cellar_mult) + (barab_temp*barab_mult) + (attic_temp*attic_mult))/(cellar_mult + barab_mult + attic_mult)
    print ("Mean temperature = %f" % mean_temp)

if __name__ == "__main__":
   read_temps() 
   
