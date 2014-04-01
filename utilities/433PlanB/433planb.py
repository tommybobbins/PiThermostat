#!/usr/bin/python
# Modified 19-Feb-2014
# tng@chegwin.org
# Plan B in case thermostat dies. Switch on heating for 2 hours per day
# if Redis queue down or thermostat is dead

import sys,time
from sys import path
import datetime
from time import sleep
from datetime import datetime
import redis
import urllib2
import re
import smtplib
sent_email=0
from email.mime.text import MIMEText
threshold_temp = 12
redthis = redis.StrictRedis(host='localhost',port=6379, db=0)


def send_email():
    SERVER = "localhost"
    FROM = "someone@someemail"
    TO = ["someoneelse@someotheremail","someoneelse2@someothermeail2"] # must be a list
    SUBJECT = "Barabbas down!"
    TEXT = "Barabbas down. I'm driving the boiler."
    # Prepare actual message
    message = """\
    From: %s
    To: %s
    Subject: %s
    
    %s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    # Send the mail
    server = smtplib.SMTP(SERVER)
    server.sendmail(FROM, TO, message)
    server.quit()
    return(1)

def run_boiler(sent_email):
    time = datetime.now().time()
    hour,min,sec = str(time).split(":")
    hour = int(hour)
    if (( hour == 10 ) | (hour == 22)):
#        print ("Firing up boiler")
        response = urllib2.urlopen("http://433board/switchboiler/on/")
#        return ("On")
        if ( sent_email == 0 ):
             send_email()
             return(1)
        else:
             return(1)
    else:
        return (0)


while True:
    outside_temp=int(redthis.get("temperature/weather"))
    if (outside_temp > threshold_temp):
#        print ("Outside temperature %i is greater than %i" %(outside_temp,threshold_temp))
         print (".")
    elif (outside_temp <= threshold_temp):
#        print ("Outside temperature %i is less than %i" %(outside_temp,threshold_temp))
#        print ("See whether we need to run boiler")
        try:
            barabbas_boiler=redthis.ttl("boiler/req")
         #   print ("Able to read redis. Queue time is : %i" % barabbas_boiler)
         #   print ("-ve means barabbas is down.")
        except:
         #   print ("Bad stuff happening. Priming email")
         #   print ("Redis down. We may need to drive the boiler.")
            sent_email=run_boiler(sent_email)
#            print ("Sent email = %i" % sent_email)
        if (barabbas_boiler < 0):
            sent_email=run_boiler(sent_email)
#            print ("Sent email = %i" % sent_email)
        else:
#            print ("Barabbas is running the boiler. Priming email")
            sent_email = 0
#            print ("Sent email = %i" % sent_email)
    sleep(240)

