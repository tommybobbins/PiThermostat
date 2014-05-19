#!/usr/bin/python
import redis
import subprocess
from time import sleep
redthis = redis.StrictRedis(host='433host',port=6379, db=0,socket_timeout=3)
allowed_jobs = ['/usr/local/bin/bgas', 
                '/usr/local/bin/homeeasy',
                '/usr/local/bin/drayton',
                '/usr/local/bin/boot_sequence.sh',
                '/usr/local/bin/half_open.sh',
                '/usr/local/bin/full_open.sh',
                '/usr/local/bin/full_to_half_open.sh',
                '/usr/local/bin/close.sh']

while True:
    try:
        # Check for permission to run 
        job_running = redthis.get('shared/jobqueue')
        if job_running:
            # We don't have permission
            #            print ("Sleeping because we have a shared/jobqueue")
            sleep(5)
            continue 
        job_to_run = redthis.lpop('cellar/jobqueue') 
#        job_to_run = redthis.lindex('attic/jobqueue', 0) 
       # print ("Job to run is %s" % job_to_run)
        if (job_to_run):
            #print ("We have a job to run")
            job_running = redthis.set('shared/jobqueue', 'True')
            job_to_run = job_to_run.split() # We only want the binary name, not the arguments
            if job_to_run[0]  in allowed_jobs:
                # We do have permission
                # print ("Shellscript to run is %s \n" % job_to_run[0]) 
                subprocess.call(job_to_run) 
                sleep(2)
                job_running = redthis.delete('shared/jobqueue')
            else: 
       #         print ("Sorry, we are not allowd to run %s \n" % job_to_run[0])
                job_running = redthis.delete('shared/jobqueue')
                continue
        else:
       #     print ("Idling")
            sleep(1)
    except:
       #     print ("Unable to read from redis")
            sleep(10)
