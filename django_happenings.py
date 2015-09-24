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
from ConfigParser import SafeConfigParser
parser = SafeConfigParser()
parser.read('/etc/pithermostat.conf')

debug=parser.get('main','debug') # As string
Debug = {'True': True, 'False': False}.get(debug, False) # As Boolean

redishost=parser.get('redis','broker')
redisport=int(parser.get('redis','port'))
redisdb=parser.get('redis','db')
redistimeout=float(parser.get('redis','timeout'))
apacheaddress=parser.get('apache','address')
apacheport=int(parser.get('apache','port'))


def parse_calendar():
     target_temp = 14;
     calendar_url = ("http://%s:%i/current/" % (apacheaddress,apacheport))
#     print ("Calendar url = %s\n" % calendar_url)
     response = urllib2.urlopen(calendar_url)
     regex_temp = re.compile(r'^\s+Temp=(.*)\s+$')
     html = response.readlines()
     for line in html:
#        print line
        match = regex_temp.search(line)
        if match:
            target_temp = float(match.group(1))
#            print ("We got match %s " % target_temp);
            return(target_temp);
     if (target_temp == 14):
        print ("Error");
        return (16.99999);

         

desired_temp=parse_calendar()
#print ("%f" % desired_temp)
