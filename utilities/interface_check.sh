#!/bin/bash

/bin/ping -c3 -q 192.168.1.254 >/dev/null
OUTPUT_PING=$?
#echo "Output ping = ${OUTPUT_PING}"

if [ ${OUTPUT_PING} -ne 0 ]
then
    logger -plocal7.notice "Interface down"
    sudo ifdown wlan0
    sudo ifup wlan0
    
fi
