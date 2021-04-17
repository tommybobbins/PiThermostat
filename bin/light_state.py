#!/usr/bin/python3

#####Parses the relay output to return the state. Switches relay if state change required ######
import re
import fileinput
import datetime
import time
import urllib3
http = urllib3.PoolManager()
import configparser
config = configparser.ConfigParser()
config.read('/etc/pithermostat.conf')

debug=config.get('main','debug') # As string
Debug = {'True': True, 'False': False}.get(debug, False) # As Boolean
Debug = True

import json

#relay_url={}
livinglight_url = {
    'livinglight': config.get('relays','livinglight') ,
}

def get_light(light):

     this_url = livinglight_url[light]
     if Debug:
        print ("This URL = %s" % this_url)
     my_url = ("http://%s/light/0" % (this_url))
     if Debug:
        print ("Light url for %s = %s\n" % (light,my_url))
     try:
        response = http.request('GET', my_url, timeout=urllib3.Timeout(connect=1.0))
        data=(json.loads(response.data.decode('utf-8')))
        #print (data)
        return (data["ison"],data["brightness"])
     except:
        return ("Error")




#$ curl http://192.168.0.77/light/0/?brightness=20
#{"ison":false,"source":"http","has_timer":false,"timer_started":0,"timer_duration":0,"timer_remaining":0,"mode":"white","brightness":20}
#$ curl http://192.168.1.203/relay/0?turn=off
#{"ison":false, "has_timer":false}
#$ curl http://192.168.1.203/relay/0
#{"ison":false, "has_timer":false}
#$ curl http://192.168.0.77/light/0/?ison=true
#{"ison":false,"source":"http","has_timer":false,"timer_started":0,"timer_duration":0,"timer_remaining":0,"mode":"white","brightness":20}
#$ curl http://192.168.0.77/light/0/?turn=on
#{"ison":true,"source":"http","has_timer":false,"timer_started":0,"timer_duration":0,"timer_remaining":0,"mode":"white","brightness":20}

def send_light(light,requested_onoff,requested_brightness):
     this_url = livinglight_url[light]
     requested_onoff=onoroff.lower()
     requested_brightness=int(requested_brightness)
     (current_onoff,current_brightness)=(get_light(light))
     if Debug:
        print ("Current state of %s is %s = %i" % (relay, current_onoff, current_brightness))
        print ("Requested state of %s is %s" % (light, requested_onoff, requested_brightness))
     if ( current_onoff != requested_onoff ):
         if Debug:
            print ("Need a change because current_onoff=%s and requested_onoff=%s" % (current_onoff,requested_onoff))
         light_url = ("http://%s/light/0?turn=%s" % (this_url,requested_onoff))
         if Debug:
            print ("Changing Light url = %s" % light_url)
         response = http.request('GET', light_url, timeout=urllib3.Timeout(connect=1.0))
         data=(json.loads(response.data.decode('utf-8')))
         return (data["ison"])
     else:
         if Debug:
            print ("Nothing to do")
         return ("Nochange")
         

#boiler_onoff=get_relay("boiler")
#water_onoff=get_relay("water")
(lighton,lightbright)=get_light("livinglight")
print ("Light is = %s and Brightness=%i" % (lighton,lightbright))
send_light("light","True",100)
#print ("Boiler = %s" % boiler_onoff)
#print ("Water = %s" % water_onoff)
#send_relay("boiler","off")
