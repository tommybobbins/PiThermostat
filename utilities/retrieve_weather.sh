#!/bin/bash
# EGNM is Leeds/Bradford airport
nice -n 15 /usr/bin/weather EGNM >/tmp/weather_conditions.txt
nice -n 15 /usr/local/bin/parse_weather.py
#curl -o /tmp/tempschedule.txt "http://django/schedule/calendar/cdaily/thermostat/"
