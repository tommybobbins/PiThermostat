#!/bin/bash
/usr/bin/sudo python /home/pi/PiThermostat/utilities/listcalendars2.py  | /bin/grep thermostat
RESULT=$?
USER_EMAIL="your@address.here"

if [ ${RESULT} -ne 0 ]
then
/usr/bin/mail -s 'Google calendar down' ${USER_EMAIL} <<EOF
Google calendar probably down. Run /home/pi/PiThermostat/utilities/listcalendars2.py and follow the instructions carefully. sample.dat should be then placed into /etc/google_calendar
.

EOF
fi
