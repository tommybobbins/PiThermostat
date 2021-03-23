#!/usr/bin/python3
# Modified 27-Sep-2015
# tng@chegwin.org

from time import sleep
import redis
import re
# Modularised, added config file, made generic
import configparser
parser = configparser.ConfigParser()
parser.read('/etc/pithermostat.conf')

redishost=parser.get('redis','broker')
redisport=int(parser.get('redis','port'))
redisdb=parser.get('redis','db')
redistimeout=float(parser.get('redis','timeout'))
redthis=redis.StrictRedis(host=redishost,port=redisport, db=redisdb, socket_timeout=redistimeout)
debug=parser.get('main','debug') # As string
Debug = {'True': True, 'False': False}.get(debug, False) # As Boolean

temperatures={}
ext_temperatures={}
multipliers={}
ext_multipliers={}
regex_temp = re.compile(r'^temperature\/(.*)\/sensor$')
# Find all the keys matching temperature/*/sensor
# For each key find, the sensor value and the multiplier value and store
# in temperatures and multipliers

def calculate_weighted_mean(incoming_multiplier,incoming_temp):
    numerator = 0
    denominator = 0
    running_mean = 14.666
    for item in incoming_temp:
        if Debug:
            print (item)
            print ("Multiplier = %f" %  float(incoming_multiplier[item]))
            print ("Temperature = %f" % float(incoming_temp[item]))
        try:
            numerator += incoming_multiplier[item]*incoming_temp[item] 
            denominator += incoming_multiplier[item] 
            running_mean =  float(numerator/denominator)
            if Debug:
                print ("numerator = %i" % numerator)
                print ("Running mean %f " % running_mean)
                print ("denominator = %i" % denominator)
        except:
            print ("Something went wrong\n")
            running_mean = 14.665
            if Debug:
                print ("numerator = %i" % numerator)
                print ("denominator = %i" % denominator)
    return(running_mean) 

def calculate_temps():
    int_temperatures={}
    ext_temperatures={}
    int_multipliers={}
    ext_multipliers={}
    regex_temp = re.compile(r'^temperature\/(.*)\/sensor$')
    # Find all the keys matching temperature/*/sensor
    # For each key find, the sensor value and the multiplier value and store
    # in temperatures and multipliers
    all_tempkeys=(redthis.keys(pattern="temperature/*/sensor"))
    for key in all_tempkeys:
        tempkey = key.decode('UTF-8')
        if Debug: 
           print ("Tempkey = %s" % tempkey)
        try:
            match = regex_temp.search(str(tempkey))
            location=match.group(1)
            if Debug:
               print ("location = %s " % location)
            zonelocation=(redthis.get('temperature/%s/zone' % location).decode('UTF-8'))
            if Debug:
               print ("zonelocation = %s " % zonelocation)
            multvalue=float(redthis.get('temperature/%s/multiplier' % location).decode('UTF-8'))
            if Debug:
               print ("multiplier = %s " % multvalue)
            if (zonelocation != "outside"):
               int_multipliers[location]=multvalue
               value=float(redthis.get(tempkey))
               int_temperatures[location]=value
            elif (zonelocation == "outside"):
               ext_multipliers[location]=multvalue
               value=float(redthis.get(tempkey))
               ext_temperatures[location]=value
        except:
            print ("Unable to determine location for %s" % tempkey)
            multipliers[tempkey]=0.1
            ext_multipliers[tempkey]=0.1
            temperatures[tempkey]=10.0
            ext_temperatures[tempkey]=8.0


    if Debug:
        print (int_temperatures)
        print (ext_temperatures)
        print (int_multipliers)
        print (ext_multipliers)
#        print ("Internal Weighted mean = %f " % weighted_mean)
#        print ("External Weighted mean = %f " % ext_weighted_mean)
    int_weighted_mean=14.333
    int_weighted_mean=float(calculate_weighted_mean(int_multipliers,int_temperatures))
    ext_weighted_mean=10.012
    ext_weighted_mean=float(calculate_weighted_mean(ext_multipliers,ext_temperatures))
    return (int_weighted_mean, ext_weighted_mean)

if Debug:
    int,ext=calculate_temps()
    print ("##################################")
    print (int)
    print ("##################################")
    print (ext)
