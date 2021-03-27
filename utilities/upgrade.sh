#!/bin/bash
cd /home/pi/PiThermostat
GIT_PULL_OUT=$(git pull 2>&1)
if [ "${GIT_PULL_OUT}" != "Already up to date." ] 
echo ${GIT_PULL_OUT}
then
   echo "No need to do anything. $GIT_PULL_OUT"
   exit 0
else
   echo "Git pull out is ${GIT_PULL_OUT}"
   make django binaries restart_daemons	
fi
