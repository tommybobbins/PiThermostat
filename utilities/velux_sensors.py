#!/usr/bin/python
import redis
import subprocess
from time import sleep
redthis = redis.StrictRedis(host='433host',port=6379, db=0, socket_timeout=3)
#allowed_jobs = ['/usr/local/bin/half_open.sh', '/usr/local/bin/full_open.sh', '/usr/local/bin/close.sh','/bin/true']

while True:
    try: 
        boiler_on = redthis.get('boiler/req2') 
        attic_temp = float(redthis.get('temperature/attic/sensor'))
        attic_temp = float(redthis.get('temperature/attic/sensor'))
        velux_close_trigger = float(redthis.get('temperature/trigger/velux/close'))
        velux_half_open_trigger = float(redthis.get('temperature/trigger/velux/half')) 
        velux_full_open_trigger = float(redthis.get('temperature/trigger/velux/full'))
        velux_state = (redthis.get('velux/3'))
        if (boiler_on != "True"):
            print ("Attic temp = %f" % attic_temp)
            if (attic_temp <= velux_half_open_trigger):
                job_to_run = "/usr/local/bin/close.sh"
                print ("Trigger temp <= %f" % velux_half_open_trigger)
                redthis.set('/velux/3','Shut')
            elif (attic_temp >=  velux_half_open_trigger):
                job_to_run = "/usr/local/bin/half_open.sh"
                print ("Trigger temp >= %f" % velux_half_open_trigger)
                redthis.set('/velux/3','Half')
            elif (attic_temp >=  velux_full_open_trigger):
                job_to_run = "/usr/local/bin/full_open.sh"
                print ("Trigger temp >= %f" % velux_full_open_trigger)
                redthis.set('/velux/3','Open')
            else:
                job_to_run = "/usr/local/bin/close.sh"
                print ("Something went wrong")
                redthis.set('/velux/3','Shut')
        else:
            job_to_run = "/usr/local/bin/close.sh"
    except:
            job_to_run = "/usr/local/bin/close.sh"
     
    redthis.expire("velux/3", 300 )
    print ("Shellscript to run is %s \n" % job_to_run) 
    sleep(10)
#   subprocess.call(job_to_run) 
