#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import json
import time
import urllib
import redis
from PIL import Image, ImageFont
from ConfigParser import SafeConfigParser

try:

    parser = SafeConfigParser()
    parser.read('/etc/pithermostat.conf')
    redishost=parser.get('redis','broker')
    redisport=int(parser.get('redis','port'))
    redisdb=parser.get('redis','db')
    redistimeout=float(parser.get('redis','timeout'))
    room_location = parser.get('locale','location')
    redthis=redis.StrictRedis(host=redishost,
                              port=redisport,  
                              db=redisdb, 
                              socket_timeout=redistimeout)
except:
    import inkyphat
    inkyphat.set_border(inkyphat.BLACK)
    inkyphat.text((36, 12), "No WiFi", inkyphat.WHITE, font=font)
    inkyphat.show()
    exit("Unable to read from /etc/pithermostat.conf")

try:
    import requests
except ImportError:
    exit("This script requires the requests module\nInstall with: sudo pip install requests")

import inkyphat


inkyphat.set_border(inkyphat.BLACK)

CITY = "Bradford"
COUNTRYCODE = "GB"
WARNING_TEMP = 30.0


def get_location():
    res = requests.get('http://ipinfo.io')
    if(res.status_code == 200):
        json_data = json.loads(res.text)
        return json_data
    return {}

# Python 2 vs 3 breaking changes.
def encode(qs):
    val = ""
    try:
        val = urllib.urlencode(qs).replace("+","%20")
    except:
        val = urllib.parse.urlencode(qs).replace("+", "%20")
    return val

icons = {}
masks = {}

location_string = "{city}, {countrycode}".format(city=CITY, countrycode=COUNTRYCODE)

weather = "?"

icon_map = {
	"snow": [5, 6, 7, 8, 10, 13, 14, 15, 16, 17, 18, 41, 42, 43, 46],
	"rain": [9, 11, 12],
	"cloud": [19, 20, 21, 22, 25, 26, 27, 28, 29, 30, 44],
	"sun": [32, 33, 34, 36],
	"storm": [0, 1, 2, 3, 4, 37, 38, 39, 45, 47],
        "wind": [23, 24]
}

pressure = 0
local_temperature = 0
mean_temperature = 0

try:
    sensor_name="temperature/"+room_location+"/sensor"
    local_temperature = float(redthis.get(sensor_name))
    mean_temperature = float(redthis.get("temperature/inside/weightedmean"))
    outside_temperature = float(redthis.get("temperature/outside/weightedmean"))
    boiler_state = (redthis.get("boiler/req"))
except:
    local_temperature=0
    mean_temperature=0
    outside_temperature=0
    boiler_state = False

weather_icon = None
bob_icon = None

# Load the built-in FredokaOne font
font = ImageFont.truetype(inkyphat.fonts.FredokaOne, 20)
font2 = ImageFont.truetype(inkyphat.fonts.FredokaOne, 18) 

# Load our backdrop image
inkyphat.set_image("resources/backdrop.png")


# Let's draw some lines!
#inkyphat.line((69, 36, 69, 81)) # Vertical line
#inkyphat.line((31, 35, 184, 35)) # Horizontal top line
#inkyphat.line((69, 58, 174, 58)) # Horizontal middle line
#inkyphat.line((169, 58, 169, 58), 2) # Red seaweed pixel :D

# And now some text

datetime = time.strftime("%d %b %Y")

inkyphat.text((50, 3), datetime, inkyphat.WHITE, font=font2)

inkyphat.text((160, 24), u"{:.1f}°".format(local_temperature), inkyphat.WHITE if local_temperature < WARNING_TEMP else inkyphat.RED, font=font)
inkyphat.text((165, 48), u"{:.1f}°".format(mean_temperature), inkyphat.WHITE if mean_temperature < WARNING_TEMP else inkyphat.RED, font=font)

inkyphat.text((1, 72), u"{:.1f}°".format(outside_temperature), inkyphat.WHITE, font=font)

inkyphat.text((1, 1), "?", inkyphat.RED, font=font)

if boiler_state == "True":
    bob_name = "resources/bob_2colour_tiny.png"
    bob_image = Image.open(bob_name)
    bob_mask = inkyphat.create_mask(bob_image)
    inkyphat.paste(bob_image, (50, 55), bob_mask)

# And show it!
inkyphat.show()
