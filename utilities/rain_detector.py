#!/usr/bin/python

import RPi.GPIO as GPIO
import redis
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN)
from time import sleep
redthis = redis.StrictRedis(host='433host',port=6379, db=0, socket_timeout=3)
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


