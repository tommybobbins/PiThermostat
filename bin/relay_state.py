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


redishost=config.get('redis','broker')
redisport=int(config.get('redis','port'))
redisdb=config.get('redis','db')
redistimeout=float(config.get('redis','timeout'))
boiler_relay=config.get('relays','boiler')
water_relay=config.get('relays','water')
#relay_url[boiler]=config.get('relays','boiler')
#relay_url[water]=config.get('relays','water')
import json

#relay_url={}
relay_url = {
    'boiler': config.get('relays','boiler') ,
    'water': config.get('relays','water') 
}

def get_relay(relay):

#$ curl http://192.168.1.203/relay/0?turn=off
#{"ison":false, "has_timer":false}
#$ curl http://192.168.1.203/relay/0
#{"ison":false, "has_timer":false}

     this_url = relay_url[relay]
     if Debug:
        print ("This URL = %s" % this_url)
     my_url = ("http://%s/relay/0" % (this_url))
     if Debug:
        print ("Relay url for %s = %s\n" % (relay,my_url))
     try:
        response = http.request('GET', my_url)
        data=(json.loads(response.data.decode('utf-8')))
        #print (data)
        return (data["ison"])
     except:
        return ("Error")

def send_relay(relay,onoroff):
#$ curl http://192.168.1.203/relay/0?turn=off
#{"ison":false, "has_timer":false}

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
         response = http.request('GET', relay_url)
         data=(json.loads(response.data.decode('utf-8')))
         return (data["ison"])
     else:
         if Debug:
            print ("Nothing to do")
         return ("Nochange")
         

#boiler_onoff=get_relay("boiler")
#water_onoff=get_relay("water")
#print ("Boiler = %s" % boiler_onoff)
#print ("Water = %s" % water_onoff)
#send_relay("water","off")
#send_relay("boiler","off")
