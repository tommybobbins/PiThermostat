#!/usr/bin/python3

import unittest
import urllib3
http = urllib3.PoolManager()

class TestSum(unittest.TestCase):

    def test_homepage(self):
        r = http.request('GET', "http://hotf/")
        self.assertEqual(r.status, 200, "Should be 200") 

    def test_cal(self):
        r = http.request('GET', "http://hotf/feed/calendar/upcoming/1/")
        self.assertEqual(r.status, 200, "Should be 200") 
    
    def test_redis(self):
        import configparser 
        import redis
        parser = configparser.ConfigParser()
        parser.read('/etc/pithermostat.conf')
        redishost=parser.get('redis','broker')
        redisport=parser.get('redis','port')
        redisdb=parser.get('redis','db')
        redistimeout=float(parser.get('redis','timeout'))
        redthis=redis.StrictRedis(host=redishost,port=redisport, db=redisdb, socket_timeout=redistimeout)
        boiler_state=redthis.get("boiler/req").decode('utf-8')
        print (boiler_state)
        self.assertEqual(boiler_state,"On|Off", "Should be On or Off")

#>>> p = re.compile('(blue|white|red)')
#>>> p.sub('colour', 'blue socks and red shoes')

#    def test_cal(self):
#        r = http.request('GET', "http://hotf/feed/calendar/upcoming/1/")
#        self.assertEqual(r.status, 200, "Should be 200") 
    
    def test_sum(self):
        self.assertEqual(sum([1, 2, 3]), 6, "Should be 6")

#    def test_sum_tuple(self):
#        self.assertEqual(sum((1, 2, 2)), 6, "Should be 6")

if __name__ == '__main__':
    unittest.main()
