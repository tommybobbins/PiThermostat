#!/bin/bash
# EGNM is Leeds/Bradford airport
/usr/bin/weather EGNM >/tmp/weather_conditions.txt 2>&1
chown pi:pi /tmp/weather_conditions.txt
