#!/usr/bin/python

import RPi.GPIO as GPIO
import redis
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN)
from time import sleep
from ConfigParser import SafeConfigParser

parser = SafeConfigParser()
parser.read('/etc/pithermostat.conf')

redishost=parser.get('redis','broker')
redisport=int(parser.get('redis','port'))
redisdb=parser.get('redis','db')
redistimeout=float(parser.get('redis','timeout'))


redthis=redis.StrictRedis(host=redishost,port=redisport, db=redisdb, socket_timeout=redistimeout)

currState = False
prevState = False

while True:
    try:
        sleep(0.1)
        prevState = currState
        currState = GPIO.input(18)
        if currState != prevState:
            newState = "HIGH" if currState else "LOW"
#            print "GPIO pin %s is %s" % (18, newState)
            try:
                redthis.set('weather/eden/rainsensor', 'True')
                redthis.expire('weather/eden/rainsensor', 14400)
            except:
                print ("Unable to update redis")
            sleep(10)
    except (KeyboardInterrupt, SystemExit):
        GPIO.cleanup()
        print ("Keyboard stop")
        exit()
    except:
        # report error and proceed
        GPIO.cleanup()
        print ("FUBAR")
        exit()


