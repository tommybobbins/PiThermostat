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
brightnessreset=int(config.get('relays','brightnessreset')) # As string
Debug = {'True': True, 'False': False}.get(debug, False) # As Boolean

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
        if Debug:
           ison=str(data["ison"]).lower()
           brightness=int(data["brightness"])
           print ("ison = %s, brightness = %i" % (ison, brightness))
        return (str(data["ison"]),int(data["brightness"]))
     except:
        return ("Error",0)


def send_light(light,requested_onoff,requested_brightness):
     this_url = livinglight_url[light]
     requested_onoff=requested_onoff.lower()
     brightness=brightnessreset # Default to 80 from /etc/pithermostat.conf
     brightness=int(requested_brightness)

     (current_onoff,current_brightness)=(get_light(light))
     current_onoff=current_onoff.lower()
     current_brightness=int(current_brightness)
     if Debug:
        print ("Current state of %s is %s = %i" % (light, current_onoff, current_brightness))
        print ("Requested state of %s is %s = %i" % (light, requested_onoff, brightness))
     switchme = "off"
     if ( current_onoff != requested_onoff ):
         requested_onoff = requested_onoff.lower()
         if ( requested_onoff == "true" ):
            switchme="on"
         elif ( requested_onoff == "false" ):
            switchme="off"
         else:
            switchme="off"
         if Debug:
            print ( "Current onoff is not equal to requested_onoff %s" % switchme )
         light_url = ("http://%s/light/0/?turn=%s&brightness=%i" % (this_url,switchme,brightness))
         if Debug:
            print (light_url)
         response = http.request('GET', light_url, timeout=urllib3.Timeout(connect=1.0))
         data=(json.loads(response.data.decode('utf-8')))
         if Debug:
            print (data["ison"], data["brightness"])
         return (data["ison"])
     elif ( current_onoff == requested_onoff ):
         if Debug:
            print ("No need to change socket state because current_onoff=%s and requested_onoff=%s. We may need to change brightness." % (current_onoff,requested_onoff))
         if ( current_brightness != requested_brightness ):
            light_url = ("http://%s/light/0/?brightness=%i" % (this_url,brightness))
            if Debug:
               print ("We need to make a change to brightness %s" % light_url)
            response = http.request('GET', light_url, timeout=urllib3.Timeout(connect=1.0))
            data=(json.loads(response.data.decode('utf-8')))
            return (data["brightness"])
         elif ( current_onoff != requested_onoff ):
            print ("Something went wrong as current_onoff is not requested_onoff. Wrong loop")
         else:  
            if Debug:
               print ("Nothing to do")
            return ("Nochange")
     else:
         if Debug:
            print ("Nothing to do")
         return ("Nochange")
         

#(lighton,lightbright)=get_light("livinglight")
#print ("Light is = %s and Brightness=%i" % (lighton,lightbright))
#state=send_light("livinglight","true",79)
#(lighton,lightbright)=get_light("livinglight")
#print ("Light is = %s and Brightness=%i" % (lighton,lightbright))
