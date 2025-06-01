#!/usr/bin/python3
# Modified 27-Sep-2015
# tng@chegwin.org

import redis
import configparser
import sys
sys.path.append('/usr/local/python/lib')
from pithermostat.logging_helper import debug_log, info_log, error_log, warning_log
import re
import datetime
import time
import urllib3
http = urllib3.PoolManager()
target_temp=14.3141
from bs4 import BeautifulSoup
#features="xml"
import sys

parser = configparser.ConfigParser()
parser.read('/etc/pithermostat.conf')

regex_temp = re.compile(r'<title>\w+=(\w+)</title>')
redishost=parser.get('redis','broker')
redisport=int(parser.get('redis','port'))
redisdb=parser.get('redis','db')
redistimeout=float(parser.get('redis','timeout'))
redthis=redis.StrictRedis(host=redishost,port=redisport, db=redisdb, socket_timeout=redistimeout)

apacheaddress=parser.get('apache','address')
apacheport=int(parser.get('apache','port'))

#curl -s http://hotf/feed/calendar/upcoming/1/ | sed -e 's/<item>/\n<item>/g'

def parse_calendar(calnum):
     calendar_url = ("http://%s:%i/feed/calendar/upcoming/%i/" % (apacheaddress,apacheport,calnum))
     debug_log("Calendar url = %s\n" % calendar_url)
     try:
         response = http.request('GET', calendar_url)
         soup = BeautifulSoup(response.data, 'xml')
         my_title = str(soup.find_all('title')[1])
         debug_log("Title = %s\n" % my_title)
         match = regex_temp.findall(my_title)
         print("Match = %s\n" % match)
         debug_log("Match = %s\n" % match)
         if match:
            debug_log("Found calendar match")
            calendar_temperature=(match[0])
            debug_log("Calendar value: %s\n" % calendar_temperature)
            return (calendar_temperature)
         else:
            debug_log("No matches found = %s\n" % calendar_url)
            return (16.88888)
     except:
         debug_log("Something went wrong pattern matching = %s\n" % calendar_url)
         return (16.99999);

def calculate_heating_water():
    try:
        debug_log("Calculating heating water schedule")
        desired_temp=parse_calendar(1)
        debug_log("%s" % desired_temp)
        desired_temp=parse_calendar(2)
        debug_log("%s" % desired_temp)
    except Exception as e:
        error_log(f"Error calculating heating water schedule: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        calculate_heating_water()
    except Exception as e:
        error_log(f"Fatal error: {str(e)}")
        sys.exit(1)
