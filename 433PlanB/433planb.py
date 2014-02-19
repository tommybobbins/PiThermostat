#!/usr/bin/python
# Modified 19-Feb-2014
# tng@chegwin.org
# Plan B in case thermostat dies. Switch on heating for 2 hours per day
# if Redis queue down or thermostat is dead

import sys,time
from sys import path
import datetime
from time import sleep
from datetime import datetime
import redis
import urllib2
import re
threshold_temp = 12
sys.path.append("/usr/local/lib/python2.7/site-packages/Adafruit/I2C")
redthis = redis.StrictRedis(host='localhost',port=6379, db=0)


def run_boiler():
    time = datetime.now().time()
    hour,min,sec = str(time).split(":")
    hour = int(hour)
    if (( hour == 10 ) | (hour == 23)):
#        print ("Firing up boiler")
        response = urllib2.urlopen("http://433board/switchboiler/on/")
        return ("On")
    else:
        return ("Done")


while True:
    outside_temp=int(redthis.get("temperature/weather"))
    if (outside_temp > threshold_temp):
#        print ("Outside temperature %i is greater than %i" %(outside_temp,threshold_temp))
        exit()
    elif (outside_temp <= threshold_temp):
#        print ("Outside temperature %i is less than %i" %(outside_temp,threshold_temp))
#        print ("See whether we need to run boiler")
        try:
            barabbas_boiler=redthis.ttl("boiler/req")
            print ("Able to read redis. Queue time is : %i" % barabbas_boiler)
            print ("-ve means barabbas is down.")
        except:
            print ("Redis down. We may need to drive the boiler.")
            run_boiler()
        if (barabbas_boiler < 0):
            run_boiler()
    sleep(240)

