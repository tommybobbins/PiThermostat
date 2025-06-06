#!/usr/bin/python3
# Modified 27-Sep-2015
# tng@chegwin.org

import redis
import subprocess
from time import sleep
import configparser
import sys
sys.path.append('/usr/local/python/lib')
from pithermostat.logging_helper import debug_log, info_log, error_log, warning_log

parser = configparser.ConfigParser()
parser.read('/etc/pithermostat.conf')

redishost=parser.get('redis','broker')
redisport=int(parser.get('redis','port'))
redisdb=parser.get('redis','db')
redistimeout=float(parser.get('redis','timeout'))

redthis=redis.StrictRedis(host=redishost,port=redisport, db=redisdb, socket_timeout=redistimeout)

allowed_jobs = ['/usr/local/bin/bgas', 
                '/usr/local/bin/homeeasy',
                '/usr/local/bin/drayton',
                '/usr/local/bin/energenie',
                '/usr/local/bin/light',
                '/usr/bin/ssh',
                '/etc/init.d/sensortag.sh',
                '/usr/local/bin/boot_sequence.sh',
                '/usr/local/bin/energenie',
                '/usr/local/bin/half_open.sh',
                '/usr/local/bin/open_to_half_open.sh',
                '/usr/local/bin/full_open.sh',
                '/usr/local/bin/closed_to_half_open.sh',
                '/usr/local/bin/all_open.sh',
                '/usr/local/bin/all_close.sh',
                '/usr/local/bin/all_half.sh',
                '/usr/local/bin/switch_tradfri.sh',
                '/usr/local/bin/full_close.sh']

def read_redis_data():
    try:
        debug_log("Reading Redis data")
        while True:
            try:
                # Check for permission to run 
                job_running = redthis.get('shared/jobqueue')
                if job_running:
                    # We don't have permission
                    #            print ("Sleeping because we have a shared/jobqueue")
                    sleep(2)
                job_to_run = (redthis.lpop('cellar/jobqueue')).decode('UTF-8')
    #        job_to_run = redthis.lindex('attic/jobqueue', 0) decode('UTF-8')
                print ("Job to run is %s" % job_to_run)
                if (job_to_run):
                    #print ("We have a job to run")
                    job_running = redthis.set('shared/jobqueue', 'True')
            except:
                debug_log("Something went wrong with the jobqueue permissions")
        # Check for permission to run 
        job_running = redthis.get('shared/jobqueue')
        if job_running:
            # We don't have permission
            #            print ("Sleeping because we have a shared/jobqueue")
            sleep(2)
        job_to_run = (redthis.lpop('cellar/jobqueue')).decode('UTF-8')
#        job_to_run = redthis.lindex('attic/jobqueue', 0) decode('UTF-8')
        print ("Job to run is %s" % job_to_run)
        if (job_to_run):
            #print ("We have a job to run")
            job_running = redthis.set('shared/jobqueue', 'True')
            job_running = redthis.expire('shared/jobqueue', 20) # We don't want to lock the jobqueue for long periods
            job_to_run = job_to_run.split() # We only want the binary name, not the arguments
            if job_to_run[0]  in allowed_jobs:
                # We do have permission
                print ("Shellscript to run is %s \n" % job_to_run[0]) 
                subprocess.call(job_to_run) 
                sleep(1)
                job_running = redthis.delete('shared/jobqueue')
            else: 
                print ("Sorry, we are not allowd to run %s \n" % job_to_run[0])
                job_running = redthis.delete('shared/jobqueue')
                sleep(0.2)
        else:
       #     print ("Idling")
            sleep(1)
    except:
       #     print ("Unable to read from redis")
            sleep(1)
