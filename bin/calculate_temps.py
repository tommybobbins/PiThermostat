#!/usr/bin/python3
# Modified 27-Sep-2015
# tng@chegwin.org

from time import sleep
import redis
import re
# Modularised, added config file, made generic
import configparser
from pithermostat.logging_helper import debug_log, info_log, error_log

parser = configparser.ConfigParser()
parser.read('/etc/pithermostat.conf')

redishost=parser.get('redis','broker')
redisport=int(parser.get('redis','port'))
redisdb=parser.get('redis','db')
redistimeout=float(parser.get('redis','timeout'))
redthis=redis.StrictRedis(host=redishost,port=redisport, db=redisdb, socket_timeout=redistimeout)

temperatures={}
ext_temperatures={}
multipliers={}
ext_multipliers={}
regex_temp = re.compile(r'^temperature\/(.*)\/sensor$')

def calculate_weighted_mean(incoming_multiplier,incoming_temp):
    numerator = 0
    denominator = 0
    running_mean = 14.666
    for item in incoming_temp:
        debug_log(f"Processing item: {item}")
        debug_log(f"Multiplier = {float(incoming_multiplier[item])}")
        debug_log(f"Temperature = {float(incoming_temp[item])}")
        try:
            numerator += incoming_multiplier[item]*incoming_temp[item] 
            denominator += incoming_multiplier[item] 
            running_mean =  float(numerator/denominator)
            debug_log(f"numerator = {numerator}")
            debug_log(f"Running mean {running_mean}")
            debug_log(f"denominator = {denominator}")
        except:
            error_log("Something went wrong in calculate_weighted_mean")
            running_mean = 14.665
            debug_log(f"numerator = {numerator}")
            debug_log(f"denominator = {denominator}")
    return(running_mean) 

def calculate_temps():
    int_temperatures={}
    ext_temperatures={}
    int_multipliers={}
    ext_multipliers={}
    regex_temp = re.compile(r'^temperature\/(.*)\/sensor$')
    all_tempkeys=(redthis.keys(pattern="temperature/*/sensor"))
    for key in all_tempkeys:
        tempkey = key.decode('UTF-8')
        debug_log(f"Tempkey = {tempkey}")
        try:
            match = regex_temp.search(str(tempkey))
            location=match.group(1)
            debug_log(f"location = {location}")
            zonelocation=(redthis.get('temperature/%s/zone' % location).decode('UTF-8'))
            debug_log(f"zonelocation = {zonelocation}")
            multvalue=float(redthis.get('temperature/%s/multiplier' % location).decode('UTF-8'))
            debug_log(f"multiplier = {multvalue}")
            if (zonelocation != "outside"):
               int_multipliers[location]=multvalue
               value=float(redthis.get(tempkey))
               int_temperatures[location]=value
            elif (zonelocation == "outside"):
               ext_multipliers[location]=multvalue
               value=float(redthis.get(tempkey))
               ext_temperatures[location]=value
        except:
            error_log(f"Unable to determine location for {tempkey}")
            multipliers[tempkey]=0.1
            ext_multipliers[tempkey]=0.1
            temperatures[tempkey]=10.0
            ext_temperatures[tempkey]=8.0

    debug_log(f"Internal temperatures: {int_temperatures}")
    debug_log(f"External temperatures: {ext_temperatures}")
    debug_log(f"Internal multipliers: {int_multipliers}")
    debug_log(f"External multipliers: {ext_multipliers}")

    int_weighted_mean=14.333
    int_weighted_mean=float(calculate_weighted_mean(int_multipliers,int_temperatures))
    ext_weighted_mean=10.012
    ext_weighted_mean=float(calculate_weighted_mean(ext_multipliers,ext_temperatures))
    return (int_weighted_mean, ext_weighted_mean)

if __name__ == "__main__":
    int,ext=calculate_temps()
    info_log("##################################")
    info_log(f"Internal temperature: {int}")
    info_log("##################################")
    info_log(f"External temperature: {ext}")
