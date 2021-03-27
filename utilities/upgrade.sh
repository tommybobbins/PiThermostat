#!/bin/bash
cd /home/pi/PiThermostat
GIT_PULL_OUT=$(git pull)
echo $GIT_PULL_OUT
if [ ${GIT_PULL_OUT} != "Already up to date." ] 
then
   echo "No need to do anything. $GIT_PULL_OUT"
fi
make django binaries restart_daemons	
