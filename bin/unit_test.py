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

    def test_cal(self):
        r = http.request('GET', "http://hotf/feed/calendar/upcoming/1/")
        self.assertEqual(r.status, 200, "Should be 200")

    def test_redis_water_value(self):
        water_value=redthis.get("water/req").decode('utf-8')
        self.assertRegex(water_value, r'^on|off$' , "on or off")

    def test_redis_water_ttl(self):
        water_time=redthis.ttl("water/req")
        self.assertLessEqual(water_time, 300, "Boiler time less than 300")

    def test_redis_boiler_value(self):
        boiler_value=redthis.get("boiler/req").decode('utf-8')
        self.assertRegex(boiler_value,r'^On|Off$', "On or Off")

    def test_redis_boiler_ttl(self):
        boiler_time=redthis.ttl("boiler/req")
        self.assertLessEqual(boiler_time, 300, "Boiler time less than 300")


if __name__ == '__main__':
    unittest.main()
