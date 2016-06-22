#!/usr/bin/python
import serial,re
from time import sleep, gmtime, strftime
import pycurl
host_url = "http://433host:5537/checkinwt/"
import logging
from time import sleep
FORMAT = "%(asctime)s:%(message)s"
logging.basicConfig(filename='/home/pi/wireless_things.txt',level=logging.INFO,format=FORMAT)
#AATEMP029.5
#Wed, 15 Jun 2016 12:43:32: AATEMP020.5
#Wed, 15 Jun 2016 12:43:32: AAAWAKE----
#Wed, 15 Jun 2016 12:43:32: AABATT3.07-
#Wed, 15 Jun 2016 12:43:32: AASLEEPING-
regex_temp = re.compile(r'(\w+)TEMP(.*)')
regex_batt = re.compile(r'(\w+)BATT(.*)')
non_decimal = re.compile(r'[^\d.]+')

DEVICE = '/dev/ttyS0'
BAUD = '9600'

def post_to_433(host,node,torv,value):
    from StringIO import StringIO
    buffer = StringIO()
    req_url = StringIO()
    c = pycurl.Curl()
    req_url.write(host)
    req_url.write(node)
    req_url.write(torv)
    req_url.write(value)
    req_url.write('/')
    logging.info("Requesting %s \n" % req_url.getvalue())
    c.setopt(c.URL, req_url.getvalue())
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    c.close()
    body = buffer.getvalue()
    logging.info(body)

#print (strftime("%a, %d %b %Y %H:%M:%S: Starting\n", gmtime()))

ser = serial.Serial(DEVICE, BAUD)
while True:
#    logging.info("Checking...")
    n = ser.inWaiting()
    if n != 0:
        msg = ser.read(n)
        temps = msg.split('a')
        for temp in temps:
            tempmatch = regex_temp.search(temp)
            if tempmatch:
                try:
                    id = tempmatch.group(1)
                    idtemp = float(tempmatch.group(2))
                    logging.info ("%s returns %f degrees\n" % (id,idtemp))
                    post_to_433 (host_url, id, "/temperature/", idtemp )
                except:
                    logging.info("Unable to parse %s" % msg)
            battmatch = regex_batt.search(temp)
            if battmatch:
                try:
                    id = battmatch.group(1)
                    idvolt = (battmatch.group(2))
                    decimal_volts = re.sub('[^\d\.]+', '', idvolt)
                    #logging.info ("battery returns %s Volts\n" % decimal_volts)
                    decimal_volts = float(decimal_volts)
                    post_to_433 (host_url, id, "/voltage/", decimal_volts )
                except:
                    logging.info("Unable to parse %s" % msg)
                    logging.info ("%s battery returns %s Volts\n" % (id,decimal_volts))
    sleep(1 * 60)
