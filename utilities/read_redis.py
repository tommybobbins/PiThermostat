#!/usr/bin/python
import redis
import subprocess
from time import sleep
redthis = redis.StrictRedis(host='433host',port=6379, db=0)
allowed_jobs = ['/usr/local/bin/bgas', '/usr/local/bin/homeeasy', '/usr/local/bin/drayton', '/usr/local/bin/boot_sequence.sh', '/usr/local/bin/half_open.sh', '/usr/local/bin/close.sh', '/usr/local/bin/full_open.sh' ]
#allowed_jobs = ['/usr/local/bin/homeeasy', '/usr/local/bin/drayton']

while True:
    job_to_run = redthis.lpop('attic/jobqueue') 
#    job_to_run = redthis.lindex('jobqueue', 0) 
    if (job_to_run):
        job_to_run = job_to_run.split()
        if job_to_run[0]  in allowed_jobs:
             try:
#                print ("Shellscript to run is %s \n" % job_to_run[0]) 
                subprocess.call(job_to_run) 
             except:
#                print ("Unable to find job_to_run")
                continue
        else: 
#            print ("Sorry, we are not allowd to run %s \n" % job_to_run[0])
            continue
    else:
#        print ("Idling")
        sleep(1)
