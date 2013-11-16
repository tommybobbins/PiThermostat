#!/bin/bash
LIGHT_STATE_FILE="/sys/class/backlight/fb_ili9320/bl_power"
CURRENT_LIGHT_STATE=`cat ${LIGHT_STATE_FILE}`
if [ $1 == 'on' ]
then
        LIGHT_STATE=0
#	echo "Requested on ${CURRENT_LIGHT_STATE}"
elif [ $1 == 'off' ]
then
        LIGHT_STATE=1
#	echo "Requested off ${CURRENT_LIGHT_STATE}"
fi

if [ ${CURRENT_LIGHT_STATE} -ne  ${LIGHT_STATE} ]
then
   echo ${LIGHT_STATE}>${LIGHT_STATE_FILE}
fi
