#!/usr/bin/python3

import unittest
import urllib3
http = urllib3.PoolManager()
import configparser 
import redis
parser = configparser.ConfigParser()
parser.read('/etc/pithermostat.conf')
redishost=parser.get('redis','broker')
redisport=parser.get('redis','port')
redisdb=parser.get('redis','db')
redistimeout=float(parser.get('redis','timeout'))
redthis=redis.StrictRedis(host=redishost,port=redisport, db=redisdb, socket_timeout=redistimeout)

class TestSum(unittest.TestCase):

    def test_homepage(self):
        r = http.request('GET', "http://hotf/")
        self.assertEqual(r.status, 200, "Should be 200") 
        print ("hp test done")

    def test_cal(self):
        r = http.request('GET', "http://hotf/feed/calendar/upcoming/1/")
        self.assertEqual(r.status, 200, "Should be 200")
        print ("cal test done")

    def waterredisvalue(self):
        print ("In water")
        water_value=self.redthis.get("water/req").decode('utf-8')
        self.assertEqual(water_value,r'^on|off$' , "on or off")
#        print ("Water redis value done")

    def test_redis_ttl(self):
        boiler_time=redthis.ttl("boiler/req")
        self.assertLessEqual(boiler_time, 300, "Boiler time less than 300")
        print ("redis ttl done")

#    def water_redis_value2(self):
#        print ("In water")
#        self.assertRegex("water","water", "on or off")

    def test_redis_value(self):
        boiler_value=redthis.get("boiler/req").decode('utf-8')
        self.assertRegex(boiler_value,r'^On|Off$', "On or Off")
        print ("redis value done")

#    def water_redis_value2(self):
#        print ("In water")
#        self.assertRegex("bobbins","bobbins", "on or off")
#        water_value=redthis.get("water/req").decode('utf-8')
#        print ("Water redis value done")

if __name__ == '__main__':
    unittest.main()
