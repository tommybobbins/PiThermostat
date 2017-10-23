#!/usr/bin/python
import sqlite3 as lite
import sys
import paho.mqtt.client as mqtt
import redis
from ConfigParser import SafeConfigParser

parser = SafeConfigParser()
parser.read('/etc/pithermostat.conf')

redishost=parser.get('redis','broker')
redisport=int(parser.get('redis','port'))
redisdb=parser.get('redis','db')
redistimeout=float(parser.get('redis','timeout'))
redthis=redis.StrictRedis(host=redishost,port=redisport, db=redisdb, socket_timeout=redistimeout)

def on_connect(client, userdata, flags, rc):

    client.subscribe("temperature/+/sensor")
def on_message(client, userdata, msg):
    topic = msg.topic
    temp = msg.payload
    macaddress = str(topic.split("/")[1])
    con = None

    con = lite.connect('/usr/local/django/home.db')
    with con:
      cur = con.cursor()   
      cur.execute("SELECT * FROM lights_esp8266 where macaddress=?", [macaddress])
    
      rows = cur.fetchall()
      for row in rows:    
	name = str(row[1])
	multiplier = str(row[3])
	location = str(row[4])
	expiry = str(row[5])
	friendly = str(row[6])
        redthis.set("temperature/%s/sensor" % name,temp)
	client.publish("temperature/%s/sensor" % name,temp)
        redthis.expire("temperature/%s/sensor" % name, expiry)
        redthis.set("temperature/%s/multiplier" % name, multiplier)
        redthis.expire("temperature/%s/multiplier" % name, expiry)
        redthis.set("temperature/%s/zone" % name, location)
        redthis.expire("temperature/%s/zone" % name, expiry)
        redthis.set("temperature/%s/friendly" % name, friendly)
        redthis.expire("temperature/%s/friendly" % name, expiry)

        #print name + " Temperature: " + temp

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("192.168.1.10",1883,60)
client.loop_forever()
