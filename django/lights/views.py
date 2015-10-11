# Create your views here.
from django.utils import timezone
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.generic.list import ListView
from django.utils import timezone
from lights.models import Socket
import datetime, os
import re
import redis
from ConfigParser import SafeConfigParser

parser = SafeConfigParser()
parser.read('/etc/pithermostat.conf')

redishost=parser.get('redis','broker')
redisport=int(parser.get('redis','port'))
redisdb=parser.get('redis','db')
redistimeout=float(parser.get('redis','timeout'))

catcannon_string=parser.get('catcannon','catcannon_host')

def switch_socket(request,plug_type,set_id, plug_id, switch_onoroff):
    cb = get_object_or_404(Socket,plug_type=plug_type,set_id=set_id, plug_id=plug_id )
    cb.lastcheckin=timezone.now()
    if switch_onoroff == "on":
       cb.switch_state = True
    elif switch_onoroff == "off":
       cb.switch_state = False
    cb.save()
#    obj_list = Socket.objects(plug_id=plug_id)
##### Make the system call###########
    redthis=redis.StrictRedis(host=redishost,port=redisport, db=redisdb, socket_timeout=redistimeout)
    if (plug_type == "energenie"):
        command_to_rethis = ("/usr/local/bin/energenie %s %s %s" %(set_id,plug_id,switch_onoroff))
    elif (plug_type == "homeeasy"):
        command_to_rethis = ("/usr/local/bin/homeeasy %s %s %s" %(set_id,plug_id,switch_onoroff))
    elif (plug_type == "biard"):
        command_to_rethis = ("/usr/local/bin/light %s" %(plug_id))
    else:
        command_to_rethis = ("/usr/local/bin/energenie %s %s %s" %(set_id,plug_id,switch_onoroff))
    if cb.location == "cellar":
        redthis.rpush("cellar/jobqueue", command_to_rethis)
    elif cb.location == "attic":
        redthis.rpush("attic/jobqueue", command_to_rethis)
    else:
        redthis.rpush("cellar/jobqueue", command_to_rethis)
    return render(request, 'lights/socketswitch.html', { 'action':'switching', 'switch_socket': cb.name,'plug_type':plug_type, 'plug_id':plug_id, 'set_id':set_id, 'switch_state':cb.switch_state, 'current_location':'POWER', } )

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
    return render(request, 'lights/catcannon.html', { 'action':'switching', 'switch_state':switch_status, 'current_location':'CATCANNON', } )

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
        season = redthis.get("velux/season")
#        except:
#            season = "Winter"
        if season == "Winter":
            redthis.set("velux/season","Summer")
        else:
            redthis.set("velux/season","Winter")
        switch_status = False
    else:
        switch_status = False
    season = redthis.get("velux/season")
    velux1_state = redthis.get("velux/1")
    velux2_state = redthis.get("velux/2")
    velux3_state = redthis.get("velux/3")
    attic_temp = redthis.get("temperature/attic/sensor")
    if switch_status:
        redthis.rpush("attic/jobqueue", switch_status)
    return render(request, 'lights/velux.html', { 'action':'switching', 'switch_state':openclosestate, 'velux1_state':velux1_state, 'velux2_state':velux2_state, 'velux3_state':velux3_state, 'attic_temp':attic_temp, 'season': season, 'current_location':'VELUX', 'switch_status': switch_status, } )

def socket_list(request,corortoggle):
    try:
    	socket_list = Socket.objects.all()
    except ValueError:
        raise Http404()
    if corortoggle == 'toggle':
        template_name = 'lights/togglelist.html'
    else: 
        template_name = 'lights/togglelist.html'
    return render(request, template_name, {'sockets': socket_list,
                                           'current_location':'POWER',})

def sockets(request):
    try:
    	socket_list = Socket.objects.all()
    except ValueError:
        raise Http404()
    template_name = 'lights/togglelist.html'
    return render(request, template_name, {'sockets': socket_list})

def thermostat(request,modify=None,modify_value=0.0):
    redthis=redis.StrictRedis(host=redishost,port=redisport, db=redisdb, socket_timeout=redistimeout)
    outside_temp=round(float(redthis.get("temperature/weather")),1)
    outside_rollingmean=round(float(redthis.get("temperature/outside/rollingmean")),1)
#    required_temp=round(float(redthis.get("temperature/userrequested")),1)
    try:
        required_temp=round(float(redthis.get("holiday_countdown")),3)
    except:
        required_temp=round(float(redthis.get("temperature/userrequested")),1)

    try: 
        attic_sensor_temp=round(float(redthis.get("temperature/attic/sensor")),2)
    except:
        attic_sensor_temp=""
    try:
        barab_sensor_temp=round(float(redthis.get("temperature/barab/sensor")),2)    
    except:
        barab_sensor_temp=""
    try:
        cellar_sensor_temp=round(float(redthis.get("temperature/cellar/sensor")),2)
    except:
        cellar_sensor_temp=""
    try:
        damo_sensor_temp=round(float(redthis.get("temperature/damocles/sensor")),2)
    except:
        damo_sensor_temp=""
#    damo_sensor_press=round(float(redthis.get("pressure/damocles/sensor")),3)
#    damo_sensor_humid=round(float(redthis.get("humidity/damocles/sensor")),3)
    try:
        eden_sensor_temp=round(float(redthis.get("temperature/eden/sensor")),2)
    except:
        eden_sensor_temp=""
    try:
        forno_sensor_temp=round(float(redthis.get("temperature/forno/sensor")),2)
    except:
        forno_sensor_temp=""
    int_weighted_mean=round(float(redthis.get("temperature/inside/weightedmean")),2)
    ext_weighted_mean=round(float(redthis.get("temperature/outside/weightedmean")),2)
    calendar_temp=round(float(redthis.get("temperature/calendar")),1)
    boiler_req=(redthis.get("boiler/req"))
    thermostat_template = 'lights/thermostat_mobile.html'
    if (modify == "damoclesrepair"):
        redthis.rpush("attic/jobqueue","/etc/init.d/sensortag.sh restart")
    elif (modify == "android"):
        thermostat_template = 'lights/thermostat_android.html'
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
    return render(request,thermostat_template,{'outside': outside_temp,'required':required_temp,'int_weighted_mean':int_weighted_mean,'barab_sensor':barab_sensor_temp,'attic_sensor':attic_sensor_temp,'cellar_sensor':cellar_sensor_temp,'calendar':calendar_temp,'boiler':boiler_req,'modify':modify, 'modify_value':modify_value, 'damo_sensor':damo_sensor_temp, 'eden_sensor':eden_sensor_temp,'forno_sensor':forno_sensor_temp,'outside_rollingmean':outside_rollingmean, 'ext_weighted_mean':ext_weighted_mean, 'redirect_required': redirect_required, 'current_location':'LIFESUPPORT' })


def holding_page(request):
    return render(request,'lights/holdingpage.html')

def makeachoice(request):
    return render(request,'lights/makeachoice.html')

def current(request):
    return render(request,'lights/current_happenings.html')

def holiday(request,modify=None,modify_value=12.0):
    redthis=redis.StrictRedis(host=redishost,port=redisport, db=redisdb, socket_timeout=redistimeout)
    try:  
        holiday_temp=round(float(redthis.get("holiday_countdown")),2)
        holiday_time=redthis.ttl("holiday_countdown")
    except:
        holiday_temp=7.0
        holiday_time=0
    if (modify == "temp"):
        holiday_temp = float(modify_value)
        redthis.set("holiday_countdown",holiday_temp)
        redthis.expire("holiday_countdown",holiday_time)
    elif (modify == "days"):
        days = (float(modify_value))
        holiday_time = int(days * 24 * 60 * 60)
        redthis.set("holiday_countdown",7.0)
        holiday_temp = 7.0
        redthis.expire("holiday_countdown",holiday_time)
    days = round(float (holiday_time / (24.0 * 60.0 * 60.0)),2)
    return render(request, 'lights/holiday.html', {'holiday_temp': holiday_temp,
                                                   'seconds': holiday_time,
                                                   'days': days,
                                                   'current_location': 'TRANSPORT',
                                                   'switch_status': modify,
                                                   })

