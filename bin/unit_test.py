#!/usr/bin/python3
# Modified 27-Sep-2015
# tng@chegwin.org

import unittest
import urllib3
import redis
import configparser
import sys
sys.path.append('/usr/local/python/lib')
from pithermostat.logging_helper import debug_log, info_log, error_log, warning_log
import sys

parser = configparser.ConfigParser()
parser.read('/etc/pithermostat.conf')

redishost=parser.get('redis','broker')
redisport=int(parser.get('redis','port'))
redisdb=parser.get('redis','db')
redistimeout=float(parser.get('redis','timeout'))
redthis=redis.StrictRedis(host=redishost,port=redisport, db=redisdb, socket_timeout=redistimeout)

http = urllib3.PoolManager()

class TestSum(unittest.TestCase):

    def test_homepage(self):
        r = http.request('GET', "http://hotf/")
        self.assertEqual(r.status, 200, "Should be 200") 

    def test_cal(self):
        r = http.request('GET', "http://hotf/feed/calendar/upcoming/1/")
        self.assertEqual(r.status, 200, "Should be 200")

    def test_redis_water_value(self):
        water_value=redthis.set("water/req","on")
        water_value=redthis.get("water/req").decode('utf-8')
        self.assertRegex(water_value, r'^on|off$' , "on or off")

    def test_redis_water_ttl(self):
        redthis.expire("water/req",290)
        water_time=redthis.ttl("water/req")
        self.assertLessEqual(water_time, 300, "Boiler time less than 300")

    def test_redis_boiler_value(self):
        redthis.set("boiler/req","On")
        boiler_value=redthis.get("boiler/req").decode('utf-8')
        self.assertRegex(boiler_value,r'^On|Off$', "On or Off")

    def test_redis_boiler_ttl(self):
        redthis.expire("boiler/req",290)
        boiler_time=redthis.ttl("boiler/req")
        self.assertLessEqual(boiler_time, 300, "Boiler time less than 300")

def run_unit_tests():
    try:
        debug_log("Running unit tests")
        unittest.main()
    except Exception as e:
        error_log(f"Error in unit tests: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        run_unit_tests()
    except Exception as e:
        error_log(f"Fatal error: {str(e)}")
        sys.exit(1)
