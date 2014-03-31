#!/usr/bin/python

#####Processes a django-schedule calendar. Only useful if not using google calendar######
import re
import fileinput
import datetime
import time
from email.utils import parsedate
import urllib2
target_temp=14
#calendar_file='/tmp/tempschedule.txt'

def parse_calendar():
     response = urllib2.urlopen('http://thermo/schedule/calendar/cdaily/thermostat/')
#     response = urllib2.urlopen('http://thermo/schedule/calendar/crankers/1/')
     regex_temp = re.compile(r'^Temp=(\d+)\|(.*)\|(.*)\|')
     html = response.readlines()
#    for line in fileinput.input(calendar_file):
     for line in html:
#        print line
        match = regex_temp.search(line)
        if match:
            target_temp = int(match.group(1))
            start_time = ( match.group(2))
            end_time = ( match.group(3))
            startdatetime = (parsedate(match.group(2)))
            enddatetime = (parsedate(match.group(3)))
            structTime = time.localtime()
            timenow = datetime.datetime(*structTime[:7])
            timestart = datetime.datetime(*startdatetime[:7])
            timeend = datetime.datetime(*enddatetime[:7])
            if ((timenow > timestart) & ( timenow < timeend)):
                return target_temp

desired_temp=parse_calendar()
print ("%d" % desired_temp)
