#!/usr/bin/python
# Modified: 19-Feb-2014
# tng@chegwin.org
# Retrieve weather locally and add to Redis

import sys,time
from sys import path
import redis
import datetime
from time import sleep
import fileinput, re
weather_file='/tmp/weather_conditions.txt'
redthis = redis.StrictRedis(host='localhost',port=6379, db=0)

def queue_weather(file):
    outside_temp=0
    redthis.set("temperature/weather",0) 
#    print ("Reading weather file %s" % file)
    import fileinput,re
    regex = re.compile(r'\s+Temperature:\s+(\d+) F \((.*)\sC\)')
    for line in fileinput.input(file):
#        print (line)
        line = line.rstrip() 
#        print (line)
        match = regex.search(line)
#        print match
        if match:
            outside_temp = int(match.group(2))
            redthis.set("temperature/weather",outside_temp) 
     

queue_weather(weather_file)
