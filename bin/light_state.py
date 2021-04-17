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



def send_relay(light,onoroff,brightness):

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

     onoroff=onoroff.lower()
     current_state=str(get_relay(relay))
     if Debug:
        print ("Current state of %s is %s" % (relay, current_state))
        print ("Requested state of %s is %s" % (relay, onoroff))
     this_relay=config.get('relays',relay)
     if ( current_state == "False" and onoroff == "on" ) or ( current_state == "True" and onoroff == "off"): 
         if Debug:
            print ("Need a change because current_state=%s and onoroff=%s" % (current_state,onoroff))
         relay_url = ("http://%s/relay/0?turn=%s" % (this_relay,onoroff))
         if Debug:
            print ("Changing Relay url = %s" % relay_url)
         response = http.request('GET', relay_url, timeout=urllib3.Timeout(connect=1.0))

         data=(json.loads(response.data.decode('utf-8')))
         return (data["ison"])
     else:
         if Debug:
            print ("Nothing to do")
         return ("Nochange")
         

#boiler_onoff=get_relay("boiler")
#water_onoff=get_relay("water")
(lighton,lightbright)=get_light("livinglight")
print ("Light is = %s on/off and Brightness=%i" % lighton,lightbright)
#print ("Boiler = %s" % boiler_onoff)
#print ("Water = %s" % water_onoff)
#send_relay("water","off")
#send_relay("boiler","off")
