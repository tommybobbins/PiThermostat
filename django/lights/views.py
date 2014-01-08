# Create your views here.
from django.utils import timezone
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic.list import ListView
from django.utils import timezone
import datetime, os
import re
import redis
from lights.models import Socket, Boiler

def switch_socket(request,set_id, plug_id, switch_onoroff):
    cb = get_object_or_404(Socket,set_id=set_id, plug_id=plug_id )
    cb.lastcheckin=timezone.now()
    if switch_onoroff == "on":
       cb.switch_state = True
    elif switch_onoroff == "off":
       cb.switch_state = False
    cb.save()
#    obj_list = Socket.objects(plug_id=plug_id)
##### Make the system call###########
    redthis = redis.StrictRedis(host='localhost',port=6379, db=0)
    command_to_rethis = ("/usr/local/bin/homeeasy %s %s %s" %(set_id,plug_id,switch_onoroff))
    redthis.rpush("jobqueue", command_to_rethis)
    return render(request, 'lights/socketswitch.html', { 'action':'switching', 'switch_socket': cb.name, 'plug_id':plug_id, 'set_id':set_id, 'switch_state':cb.switch_state } )

def switch_boiler(request, switch_onoroff):
    cb = get_object_or_404(Boiler, id=1)
    cb.lastcheckin=timezone.now()
    if switch_onoroff == "on":
       cb.switch_state = True
    elif switch_onoroff == "off":
       cb.switch_state = False
    cb.save()
#    obj_list = Socket.objects(plug_id=plug_id)
##### Make the system call###########
    redthis = redis.StrictRedis(host='localhost',port=6379, db=0)
    command_to_rethis = ("/usr/local/bin/bgas %s" %(switch_onoroff))
    redthis.rpush("jobqueue", command_to_rethis)
    return render(request, 'lights/socketswitch.html', { 'action':'switching', 'switch_socket': cb.name, 'plug_id':0, 'set_id':0, 'switch_state':cb.switch_state } )

def socket_list(request,corortoggle):
    try:
    	socket_list = Socket.objects.all()
    except ValueError:
        raise Http404()
    if corortoggle == 'toggle':
        template_name = 'lights/togglelist.html'
    else: 
        template_name = 'lights/togglelist.html'
    return render(request, template_name, {'sockets': socket_list})

def sockets(request):
    try:
    	socket_list = Socket.objects.all()
    except ValueError:
        raise Http404()
    template_name = 'lights/togglelist.html'
    return render(request, template_name, {'sockets': socket_list})

def thermostat(request,modify=None,modify_value=0):
    redthis = redis.StrictRedis(host='433board',port=6379, db=0)
    outside_temp=int(redthis.get("temperature/weather"))
#    boost_temp=round(float(redthis.get("temperature/boosted")),1)
    required_temp=round(float(redthis.get("temperature/required")),1)
    sensor_temp=round(float(redthis.get("temperature/sensor")),2)
    calendar_temp=round(float(redthis.get("temperature/calendar")),1)
    boiler_req=(redthis.get("boiler/req"))
#    turbo_redis=(redthis.get("temperature/turbo"))
#    turbo_redis = True if turbo_redis =="True" else False
    thermostat_template = 'lights/thermostat.html'
#    print ("Turbo redis = %r" % turbo_redis)
    modify_value=float(modify_value)
#    boost_temp=float(boost_temp)
    if ((modify == "decrement") and modify_value):
        boost_temp = modify_value
        required_temp = float(required_temp - boost_temp)
        thermostat_template = 'lights/thermostat_action.html'
    elif (( modify == "increment" ) and modify_value):
        boost_temp = modify_value
        required_temp = float(required_temp + boost_temp)
        thermostat_template = 'lights/thermostat_action.html'
    elif (( modify == "required" ) and modify_value):
#        print ("We got a match\n")
        required_temp = float(modify_value)
        thermostat_template = 'lights/thermostat.html'
#    redthis.set("temperature/boosted",boost_temp)
    redthis.set("temperature/required",required_temp)
    return render(request,thermostat_template,{'outside': outside_temp,'required':required_temp,'sensor':sensor_temp,'calendar':calendar_temp,'boiler':boiler_req,'modify':modify, 'modify_value':modify_value, })


def holding_page(request):
    return render(request,'lights/holdingpage.html')

def makeachoice(request):
    return render(request,'lights/makeachoice.html')
