#!/usr/bin/python

import redis
import urllib2
import json
from ConfigParser import SafeConfigParser

parser = SafeConfigParser()
parser.read('/etc/pithermostat.conf')

redishost=parser.get('redis','broker')
redisport=int(parser.get('redis','port'))
redisdb=parser.get('redis','db')
redistimeout=float(parser.get('redis','timeout'))
redthis=redis.StrictRedis(host=redishost,port=redisport, db=redisdb, socket_timeout=redistimeout)

loc=parser.get('wunder', 'location')
apikey=parser.get('wunder', 'apikey')

url='http://api.wunderground.com/api/' + apikey + '/geolookup/conditions/q/pws:' + loc + '.json'
print url
f = urllib2.urlopen(url)
json_string = f.read()
parsed_json = json.loads(json_string)
temp_c = parsed_json['current_observation']['temp_c']
weather = parsed_json['current_observation']['weather']
wind_mph = parsed_json['current_observation']['wind_mph']
wind_dir = parsed_json['current_observation']['wind_dir']
redthis.set("temperature/weather",temp_c)
redthis.set("weather/weather", weather)
redthis.set("weather/wind_mph", wind_mph)
redthis.set("weather/wind_dir", wind_dir)

f.close()
