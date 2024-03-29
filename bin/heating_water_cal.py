#!/usr/bin/python3

#####Processes a django-schedule calendar. Only useful if not using google calendar######
import re
import datetime
import time
import urllib3
http = urllib3.PoolManager()
target_temp=14.3141
import configparser
parser = configparser.ConfigParser()
parser.read('/etc/pithermostat.conf')
from bs4 import BeautifulSoup

debug=parser.get('main','debug') # As string
Debug = {'True': True, 'False': False}.get(debug, False) # As Boolean

regex_temp = re.compile(r'<title>\w+=(\w+)</title>')

redishost=parser.get('redis','broker')
redisport=int(parser.get('redis','port'))
redisdb=parser.get('redis','db')
redistimeout=float(parser.get('redis','timeout'))
apacheaddress=parser.get('apache','address')
apacheport=int(parser.get('apache','port'))

#curl -s http://hotf/feed/calendar/upcoming/1/ | sed -e 's/<item>/\n<item>/g'

def parse_calendar(calnum):
     calendar_url = ("http://%s:%i/feed/calendar/upcoming/%i/" % (apacheaddress,apacheport,calnum))
     #print ("Calendar url = %s\n" % calendar_url)
     try:
         response = http.request('GET', calendar_url)
         soup = BeautifulSoup(response.data, 'html.parser')
         my_title = str(soup.find_all('title')[1])
         #print (my_title)
         match = regex_temp.findall(my_title)
         if match:
            calendar_temperature=(match[0])
             #print (calendar_temperature)
            return (calendar_temperature)
         else:
            return (16.99999)
     except:
         return (16.99999);

desired_temp=parse_calendar(1)
print ("%s" % desired_temp)
desired_temp=parse_calendar(2)
print ("%s" % desired_temp)
