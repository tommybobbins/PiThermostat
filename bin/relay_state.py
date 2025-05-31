#!/usr/bin/python3
# Modified 27-Sep-2015
# tng@chegwin.org

import redis
import configparser
from pithermostat.logging_helper import debug_log, info_log, error_log, warning_log
import re
import fileinput
import datetime
import time
import urllib3
http = urllib3.PoolManager()
import json

parser = configparser.ConfigParser()
parser.read('/etc/pithermostat.conf')

redishost=parser.get('redis','broker')
redisport=int(parser.get('redis','port'))
redisdb=parser.get('redis','db')
redistimeout=float(parser.get('redis','timeout'))
redthis=redis.StrictRedis(host=redishost,port=redisport, db=redisdb, socket_timeout=redistimeout)

boiler_relay=parser.get('relays','boiler')
water_relay=parser.get('relays','water')
#relay_url[boiler]=config.get('relays','boiler')
#relay_url[water]=config.get('relays','water')

#relay_url={}

def relay_url (device):

    try:
        relay_url = str(parser.get('relays',device))
        relay_int = int(parser.get('relays',device+"_index"))
        return (relay_url, relay_int)
    except:
        print ("Error in relay_url")
        return ("Error", "23")


def get_relay(device):

     this_device,this_index = relay_url(device)
     my_url = ("http://%s/relay/%i" % (this_device,this_index))
     try:
        response = http.request('GET', my_url, timeout=urllib3.Timeout(connect=1.0))
        data=(json.loads(response.data.decode('utf-8')))
        return (data["ison"])
     except:
        print ("Error in get_relay")
        return ("Error")

def send_relay(device,onoroff):

     this_device,this_index = relay_url(device)
     current_state=str(get_relay(device))
     if ( current_state == "False" and onoroff == "on" ) or ( current_state == "True" and onoroff == "off"): 
         built_url = ("http://%s/relay/%i?turn=%s" % (this_device,this_index,onoroff))
         response = http.request('GET', built_url, timeout=urllib3.Timeout(connect=1.0))

         data=(json.loads(response.data.decode('utf-8')))
         return (data["ison"])
     else:
         return ("Nochange")
         
#relay_url("water")
#relay_url("boiler")
#boiler_onoff=get_relay("boiler")
#water_onoff=get_relay("water")
#print ("Boiler = %s" % boiler_onoff)
#print ("Water = %s" % water_onoff)
#send_relay("water","off")
#send_relay("boiler","off")

def update_relay_state():
    try:
        debug_log("Updating relay state")
        # ... existing code ...
    except Exception as e:
        error_log(f"Error updating relay state: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        update_relay_state()
    except Exception as e:
        error_log(f"Fatal error: {str(e)}")
        sys.exit(1)
