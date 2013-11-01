#!/usr/bin/python
#from json import load
#from urllib2 import urlopen
#from pprint import pprint
import sys
sys.path.append('/usr/local/lib/python2.7/dist-packages/package/')
#data = urlopen('http://openweathermap.org/data/2.1/find/name?q=bradford&units=metric')
#cities = load(data)
#if cities['count'] > 0:
#   city = cities['list'][0]
#   pprint(city['main'])

import pyowm
#import openweathermap
from pyowm import OpenWeatherMapApi

#get the next 10 stations for a given latitude/longitude
api = OpenWeatherMapApi()
#53.848N 1.767W
stationlist = api.getstationbycoordinates(53.848, -1.767, 10)

#print the stations > 
for station in stationlist:
    print station
