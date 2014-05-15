#!/usr/bin/python
import redis
import subprocess
from time import sleep
redthis = redis.StrictRedis(host='433host',port=6379, db=0, socket_timeout=3)

while True:
    try: 
        boiler_on = redthis.get('boiler/req') 
        attic_temp = float(redthis.get('temperature/attic/sensor'))
        velux_close_trigger = float(redthis.get('temperature/trigger/velux/close'))
        velux_half_open_trigger = float(redthis.get('temperature/trigger/velux/half')) 
        velux_full_open_trigger = float(redthis.get('temperature/trigger/velux/full'))
        velux_state = (redthis.get('velux/3'))
        if (boiler_on == "True"):
#            print ("Boiler on. Need to close window")
            job_to_run = "/usr/local/bin/close.sh"
            redthis.rpush('attic/jobqueue',job_to_run)
            sleep(14400)
        else:
             sleep(0.1)
#             print ("Attic temp = %f" % attic_temp)
#             print ("Half Trigger temp = %f" % velux_half_open_trigger)
#             print ("Full Trigger temp = %f" % velux_full_open_trigger)
#             print ("Close Trigger temp = %f" % velux_close_trigger)
#             print ("Velux state = %s" % velux_state)

        if (velux_state == "Half"):
             # We can either open at higher temp or close at Close Trigger Temp
             if (attic_temp >= velux_full_open_trigger):
                 job_to_run="/usr/local/bin/full_open.sh"
             elif (attic_temp >= velux_close_trigger):
#                 print ("Nothing to do")
                 job_to_run=0
             elif (attic_temp <= velux_close_trigger):
                 job_to_run="/usr/local/bin/close.sh"
             else:
                 job_to_run="/usr/local/bin/close.sh"
        elif (velux_state == "Open"):
             # We can close at lower
             if (attic_temp >= velux_full_open_trigger):
#                 print ("Nothing to do")
                 job_to_run=0
             elif (attic_temp >= velux_close_trigger):
                 job_to_run="/usr/local/bin/full_to_half_open.sh"
             elif (attic_temp <= velux_close_trigger):
                 job_to_run="/usr/local/bin/close.sh"
             else:
                 # attic_temp between velux_c_trig and velux_h_o_trig
                 job_to_run=0
        elif (velux_state == "Closed"):
             # We can Half open at higher temp
             if (attic_temp >= velux_half_open_trigger):
                 job_to_run="/usr/local/bin/half_open.sh"
             elif (attic_temp >= velux_full_open_trigger):
                 job_to_run="/usr/local/bin/full_open.sh"
             else:
#                 print ("Nothing to do")
                 job_to_run=0
        else:
#             print ("Our velux state expired")
             # We can Half open at higher temp
             if (attic_temp >= velux_full_open_trigger):
                 job_to_run="/usr/local/bin/full_open.sh"
             elif (attic_temp <= velux_half_open_trigger):
                 job_to_run="/usr/local/bin/close.sh"
             elif (attic_temp >= velux_half_open_trigger):
                 job_to_run="/usr/local/bin/half_open.sh"
             else:
                 job_to_run="/usr/local/bin/close.sh"
  
    except:
#        print ("Something went wrong in the try")
        job_to_run = "/usr/local/bin/close.sh"
     
    try:
        if (job_to_run != 0):
#            print ("At this point we push %s to the queue \n" % job_to_run) 
            redthis.rpush('attic/jobqueue',job_to_run)
            sleep(120)
            redthis.expire("velux/3", 3600 ) #Expire in an hour
    except:
        print ("We have no job to run")
    sleep(120)
