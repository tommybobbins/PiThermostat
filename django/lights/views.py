# Create your views here.
from django.utils import timezone
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.generic.list import ListView
from django.utils import timezone
from django.core.urlresolvers import reverse
#from lights.models import Socket
from lights.models import Socket,ESP8266
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
    refresh_time=0
    left_column={}
    right_column={}
    redthis=redis.StrictRedis(host=redishost,port=redisport, db=redisdb, socket_timeout=redistimeout)
    try: 
        calendar_temp=round(float(redthis.get("temperature/calendar")),1)
        outside_temp=round(float(redthis.get("temperature/weather")),1)
        outside_rollingmean=round(float(redthis.get("temperature/outside/rollingmean")),1)
        int_weighted_mean=round(float(redthis.get("temperature/inside/weightedmean")),2)
        ext_weighted_mean=round(float(redthis.get("temperature/outside/weightedmean")),2)
        boiler_req=(redthis.get("boiler/req"))
        left_column['Calendar']=calendar_temp
        right_column['Weather']=outside_temp
        right_column['Ext. Roll']=outside_rollingmean
#        left_column['Int.W.Mean']=int_weighted_mean
#        right_column['Ext.W.Mean']=ext_weighted_mean
        left_column['Boiler']=boiler_req
    except:
        left_column['Missing values']="N/A"
    try:
        required_temp=round(float(redthis.get("holiday_countdown")),3)
    except:
        required_temp=round(float(redthis.get("temperature/userrequested")),1)
    regex_temp = re.compile(r'^temperature\/(.*)\/sensor$')
    # Find all the keys matching temperature/*/sensor
    # For each key find, the sensor value and store
    # in temperatures
    all_tempkeys=(redthis.keys(pattern="temperature/*/sensor"))
    for tempkey in all_tempkeys:
        match = regex_temp.search(tempkey)
        location=match.group(1)
        zonelocation=(redthis.get('temperature/%s/zone' % location))
        value=float(redthis.get(tempkey))
        if (zonelocation != "outside"):
            print ("Adding %s %d inside" % (location, value))
            left_column[location]=value
        elif (zonelocation == "outside"):
            print ("Adding %s %d outside " % (location, value))
            right_column[location]=value

    thermostat_template = 'lights/thermostat_mobile.html'
    if (modify == "android"):
        refresh_time=60
    elif (modify == "refresh"):
        refresh_time=float(modify_value)
    modify_value=float(modify_value)
    if (modify_value > 0.0):
        required_temp = float(modify_value)
        redthis.set("temperature/userrequested",modify_value)
        #If user selects a temperature, take it out of holiday mode too
        redthis.expire("holiday_countdown",0)
        redirect_required = True
#        return HttpResponseRedirect(reverse('polls:results', args=(p.id,))) 
    else:
        required_temp = float(required_temp)
        redirect_required = False
    left_column['Required']=required_temp
    return render(request,thermostat_template,{'modify':modify, 'modify_value':modify_value, 'redirect_required': redirect_required, 'current_location':'LIFESUPPORT', 'refresh_time':refresh_time, 'left_column':left_column, 'right_column':right_column,'int_weighted_mean':int_weighted_mean,'ext_weighted_mean':ext_weighted_mean,'Boiler':boiler_req,  })


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
                                                   'modify_value': modify,
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
        return render(request,'lights/allok.html')
    except:
        print ("Unable to set set")
