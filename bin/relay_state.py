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
#Debug = True


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

def relay_url (device):

    try:
        relay_url = str(config.get('relays',device))
        relay_int = int(config.get('relays',device+"_index"))
        if Debug:
            print (relay_url, relay_int)
        return (relay_url, relay_int)
    except:
        print ("Error in relay_url")
        return ("Error", "23")


def get_relay(device):

     this_device,this_index = relay_url(device)
     my_url = ("http://%s/relay/%i" % (this_device,this_index))
     if Debug:
        print ("Relay url for %s = %s\n" % (this_device,my_url))
     try:
        response = http.request('GET', my_url, timeout=urllib3.Timeout(connect=1.0))
        data=(json.loads(response.data.decode('utf-8')))
        if Debug:
            print (data["ison"])
        return (data["ison"])
     except:
        print ("Error in get_relay")
        return ("Error")

def send_relay(device,onoroff):

     print ("Inside send_relay for device=%s, turning %s" % (device,onoroff))
     #onoroff=onoroff.lower()
     this_device,this_index = relay_url(device)
     current_state=str(get_relay(device))
     if Debug:
        print ("Back from get_relay for device=%s with current_state=%s" % (device,current_state))
        print ("Current state of %s is %s" % (device, current_state))
        print ("Requested state of %s is %s" % (device, onoroff))
        print ("Requested index of %s is %i" % (device, this_index))
     if ( current_state == "False" and onoroff == "on" ) or ( current_state == "True" and onoroff == "off"): 
         if Debug:
            print ("Need a change because current_state=%s and onoroff=%s" % (current_state,onoroff))
         built_url = ("http://%s/relay/%i?turn=%s" % (this_device,this_index,onoroff))
         if Debug:
            print ("Changing Relay url = %s" % built_url)
         response = http.request('GET', built_url, timeout=urllib3.Timeout(connect=1.0))

         data=(json.loads(response.data.decode('utf-8')))
         return (data["ison"])
     else:
         if Debug:
            print ("Nothing to do")
         return ("Nochange")
         
#relay_url("water")
#relay_url("boiler")
#boiler_onoff=get_relay("boiler")
#water_onoff=get_relay("water")
#print ("Boiler = %s" % boiler_onoff)
#print ("Water = %s" % water_onoff)
#send_relay("water","off")
#send_relay("boiler","off")
