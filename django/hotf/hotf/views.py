# Create your views here.
from django.utils import timezone
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.generic.list import ListView
from django.utils import timezone
from django import forms

#from django.core.urlresolvers import reverse
#from lights.models import Socket
from .models import ESP8266, WirelessTemp
#from models import WirelessTemp
import datetime, os
import re
import redis
import configparser

config = configparser.ConfigParser()
config.read('/etc/pithermostat.conf')

redishost=config['redis']['broker']
redisport=int(config['redis']['port'])
redisdb=config['redis']['db']
redistimeout=int(config['redis']['timeout'])
holiday_temp = float(config['locale']['holiday_temp'])
boost_temp = float(config['locale']['boost_temp'])
boosted_time = int(config['locale']['boost_time'])

catcannon_string=config['catcannon']['catcannon_host']

def catcannon(request, switch_onoroff):
    redthis=redis.StrictRedis(host=redishost,port=redisport, db=redisdb, socket_timeout=redistimeout)
    if switch_onoroff == "on":
        switch_status="True"
        redthis.set("permission_to_fire", switch_status)
        command_to_rethis = ("/usr/bin/ssh %s /usr/bin/sudo /usr/local/bin/remote_ultra_on.sh" % catcannon_string)
        redthis.rpush("cellar/jobqueue", command_to_rethis)
    elif switch_onoroff == "off":
        switch_status="False"
        redthis.set("permission_to_fire", switch_status)
        command_to_rethis = ("/usr/bin/ssh %s /usr/bin/sudo /usr/local/bin/remote_ultra_off.sh" % catcannon_string)
        redthis.rpush("cellar/jobqueue", command_to_rethis)
    elif switch_onoroff == "status":
##### Make the system call###########
        switch_status=redthis.get("permission_to_fire")
    return render(request, 'catcannon.html', { 'action':'switching', 'switch_state':switch_status, 'current_location':'CATCANNON', } )

def velux(request, openclosestate):
    redthis=redis.StrictRedis(host=redishost,port=redisport, db=redisdb, socket_timeout=redistimeout)
    #/usr/local/bin/full_open.sh
    #/usr/local/bin/closed_to_half_open.sh  
    #/usr/local/bin/open_to_half_open.sh
    #/usr/local/bin/full_close.sh
    if openclosestate == "close":
        switch_status="/usr/local/bin/full_close.sh"
    elif openclosestate == "open":
        switch_status="/usr/local/bin/full_open.sh"
        redthis.delete("boiler/4hourtimeout")
    elif openclosestate == "half":
        switch_status="/usr/local/bin/closed_to_half_open.sh"
        redthis.delete("boiler/4hourtimeout")
    elif openclosestate == "allopen":
        switch_status="/usr/local/bin/all_open.sh"
        redthis.delete("boiler/4hourtimeout")
    elif openclosestate == "allclose":
        switch_status="/usr/local/bin/all_close.sh"
        redthis.delete("boiler/4hourtimeout")
    elif openclosestate == "allhalf":
        switch_status="/usr/local/bin/all_half.sh"
        redthis.delete("boiler/4hourtimeout")
    elif openclosestate == "toggleseason":
#        try:
        season = redthis.get("velux/season").decode('UTF-8')
#        except:
#            season = "Winter"
        if season == "Winter":
            redthis.set("velux/season","Summer")
        else:
            redthis.set("velux/season","Winter")
        switch_status = False
    else:
        switch_status = False
    season = redthis.get("velux/season").decode('UTF-8')
    velux1_state = redthis.get("velux/1")
    velux2_state = redthis.get("velux/2")
    velux3_state = redthis.get("velux/3")
    attic_temp = redthis.get("temperature/attic/sensor")
    if switch_status:
        redthis.rpush("attic/jobqueue", switch_status)
    return render(request, 'velux.html', { 'modify':openclosestate,'modify_value':openclosestate, 'action':'switching', 'switch_state':openclosestate, 'velux1_state':velux1_state, 'velux2_state':velux2_state, 'velux3_state':velux3_state, 'attic_temp':attic_temp, 'season': season, 'current_location':'VELUX', 'switch_status': switch_status, } )

def thermostat(request,modify=None,modify_value=0.0):
    refresh_time=10
    left_column={}
    right_column={}
    redthis=redis.StrictRedis(host=redishost,port=redisport, db=redisdb, socket_timeout=redistimeout)
    if (modify == "wboost"):
        water_temp = "On"
        redthis.set("water/req",water_temp)
        redthis.expire("water/req",boosted_time)
    elif (modify == "wboostoff"):
        water_temp = "Off"
        redthis.set("water/req",water_temp)
        redthis.expire("water/req",10)
    try:
        boiler_relay=redthis.get("relay/boiler").decode('UTF-8')
        water_relay=redthis.get("relay/water").decode('UTF-8')
        water_req=redthis.get("water/req").decode('UTF-8')
    except:
        boiler_relay="Lost"
        water_relay="Lost"
        water_req="Lost"
    try: 
        calendar_temp=float(redthis.get("temperature/calendar"))
#        outside_temp=float(redthis.get("temperature/weather"))
        outside_rollingmean=float(redthis.get("temperature/outside/rollingmean"))
        int_weighted_mean=float(redthis.get("temperature/inside/weightedmean"))
        ext_weighted_mean=float(redthis.get("temperature/outside/weightedmean"))
        boiler_req=redthis.get("boiler/req").decode('UTF-8')
        left_column['BoilCal']=calendar_temp
        left_column['BoilReq'] = boiler_req
        left_column['BoilOn'] = boiler_relay
        left_column['H2OCal']=water_req
        left_column['H2OOn'] = water_relay
        right_column['ExtTemp']=outside_rollingmean
    except:
        left_column['Missing values']="N/A"
        boiler_req="N/A"
    try:
        required_temp=float(redthis.get("holiday_countdown"))
    except:
        required_temp=float(redthis.get("temperature/userrequested"))
    try:
        boosted=float(redthis.get("boosted"))
    except:
        boosted=0
    regex_temp = re.compile(r'^temperature\/(.*)\/sensor$')
    # Find all the keys matching temperature/*/sensor
    # For each key find, the sensor value and store
    # in temperatures
    all_tempkeys=(redthis.keys(pattern="temperature/*/sensor"))
    for tempkey in all_tempkeys:
        match = regex_temp.search(tempkey.decode('utf-8'))
        #print ("Tempkey = %s" % tempkey)
        location=match.group(1)
        #print ("location = %s" % location)
        zonelocation=(redthis.get('temperature/%s/zone' % location)).decode('utf-8')
        #print ("Zonelocation = %s" % zonelocation)
        value=float(redthis.get(tempkey))
        if (zonelocation != "outside"):
            #print ("Adding %s %d inside" % (location, value))
            left_column[location]=value
        elif (zonelocation == "outside"):
            #print ("Adding %s %d outside " % (location, value))
            right_column[location]=value

    thermostat_template = 'thermostat_mobile.html'
    if (modify == "status"):
        refresh_time=60.0
    elif (modify == "refresh"):
        refresh_time=float(modify_value)
    else:
        refresh_time=60.0
    modify_value=float(modify_value)
    if (modify_value > 0.0):
        required_temp = float(modify_value)
        redthis.set("temperature/userrequested",modify_value)
        #If user selects a temperature, take it out of holiday mode too
        redthis.expire("holiday_countdown",0)
        redirect_required = True
    else:
        required_temp = float(required_temp)
        redirect_required = False
    left_column['Required']=required_temp
    return render(request,thermostat_template,{'modify':modify, 'modify_value':modify_value, 'redirect_required': redirect_required, 'current_location':'LIFESUPPORT', 'refresh_time':refresh_time, 'left_column':left_column, 'right_column':right_column,'int_weighted_mean':int_weighted_mean,'ext_weighted_mean':ext_weighted_mean,'Boiler':boiler_req,'boosted':boosted,'boiler_relay':boiler_relay,'water_relay':water_relay,  })


def holding_page(request):
    return render(request,'holdingpage.html')

def makeachoice(request):
    try:  
        redthis=redis.StrictRedis(host=redishost,port=redisport, db=redisdb, socket_timeout=redistimeout)
        water_relay=redthis.get("relay/water").decode('UTF-8')
    except:
        water_relay="Error"
    return render(request, 'makeachoice.html',{'current_location':"SELECT", 'water_relay':water_relay,})

def current(request):
    return render(request,'current_happenings.html')

def holiday(request,modify=None,modify_value=None):
    redthis=redis.StrictRedis(host=redishost,port=redisport, db=redisdb, socket_timeout=redistimeout)
    try:  
        holiday_temp=float(redthis.get("holiday_countdown"))
        holiday_time=redthis.ttl("holiday_countdown")
    except:
        holiday_time=0
        holiday_temp=6.666
    if (modify == "temp"):
        holiday_temp = float(modify_value)
        redthis.set("holiday_countdown",holiday_temp)
        redthis.expire("holiday_countdown",holiday_time)
    elif (modify == "boost"):
        holiday_time = 3600
        holiday_temp = float(modify_value)
        redthis.set("holiday_countdown",holiday_temp)
        redthis.expire("holiday_countdown",holiday_time)
        redthis.set("boosted",holiday_temp)
        redthis.expire("boosted",holiday_time)
    elif (modify == "days"):
        days = (float(modify_value))
        holiday_time = int(days * 24 * 60 * 60)
        redthis.set("holiday_countdown",7.0)
        redthis.expire("holiday_countdown",holiday_time)
    else:
        modify="status"
    days = float (holiday_time / (24.0 * 60.0 * 60.0))
    return render(request, 'holiday.html', {'holiday_temp': holiday_temp,
                                                   'seconds': holiday_time,
                                                   'days': days,
                                                   'current_location': 'TRANSPORT',
                                                   'modify_value': modify_value,
                                                   'modify': modify,
                                                   })

def esp_sensor(request, device='00:11:22:33:44:55', reading=15.0):
# /checkin/18:fe:34:f4:d2:77/temperature/20.1875/
    redthis=redis.StrictRedis(host=redishost,port=redisport, db=redisdb, socket_timeout=redistimeout)
    try:
        cb = get_object_or_404(ESP8266, macaddress=device)
        redthis.set("temperature/%s/sensor" % cb.name,reading)
        redthis.expire("temperature/%s/sensor" % cb.name, cb.expirytime)
        redthis.set("temperature/%s/multiplier" % cb.name, cb.multiplier)
        redthis.expire("temperature/%s/multiplier" % cb.name, cb.expirytime)
        redthis.set("temperature/%s/zone" % cb.name, cb.location)
        redthis.expire("temperature/%s/zone" % cb.name, cb.expirytime)
        return HttpResponse("Temp receive OK")
    except:
        return HttpResponse("Temp receive FAILED")

def wireless_sensor(request, device='DD', temp_or_voltage="temperature", reading=15.0):
# /checkinwt/DD/temperature/20.1875/
# /checkinwt/DD/voltage/2.875/
    redthis=redis.StrictRedis(host=redishost,port=redisport, db=redisdb, socket_timeout=redistimeout)
    try:
       cb = get_object_or_404(WirelessTemp, macaddress=device)
       if (temp_or_voltage == "temperature"):   
          redthis.set("temperature/%s/sensor" % cb.name,reading)
          redthis.expire("temperature/%s/sensor" % cb.name, cb.expirytime)
          redthis.set("temperature/%s/multiplier" % cb.name, cb.multiplier)
          redthis.expire("temperature/%s/multiplier" % cb.name, cb.expirytime)
          redthis.set("temperature/%s/zone" % cb.name, cb.location)
          redthis.expire("temperature/%s/zone" % cb.name, cb.expirytime)
          return HttpResponse("Temp received OK")
       elif (temp_or_voltage == "voltage"):
          redthis.set("voltage/%s/sensor" % cb.name,reading)
          # Voltages need to hang around in redis longer
          vexpiry = cb.expirytime*24
          redthis.expire("voltage/%s/sensor" % cb.name, vexpiry)
          return HttpResponse("Voltage received OK")
       else:
          return HttpResponse("No temperature or Voltage received")
    except:
       return HttpResponse("Temp or Voltage receive FAILED")

def bork(request, device=0, onoffstate=0):
    redthis=redis.StrictRedis(host=redishost,port=redisport, db=redisdb, socket_timeout=redistimeout)
    device = int(device)
    onoffstate = int(onoffstate)
    try: 
        if device == 0:
            return render(request, 'bork.html', { 'modify':status, 'modify_value':status, 'switch_state':onoffstate, 'current_location':'BORK', } )
        elif device  >= 1:
            switch_status = "/usr/local/bin/switch_tradfri.sh %i %i" % (device, onoffstate)
        else:
            return HttpResponse("No on/off received")
#            return render(request, 'bork.html', { 'modify_value':device, 'switch_state':onoffstate, 'current_location':'BORK', } )
        if switch_status:
            redthis.rpush("cellar/jobqueue", switch_status)
#            return HttpResponse("Device %i switched  OK" % (device))
            return render(request, 'bork.html', { 'modify':"borked", 'modify_value':switch_status, 'switch_state':onoffstate, 'current_location':'BORK', } )
        else: 
            #print ("No switch status %s" % switch_status)
            return HttpResponse("No switch status")
    except:
        return render(request, 'bork.html', { 'modify_value':device, 'switch_state':onoffstate, 'current_location':'BORK', } )

