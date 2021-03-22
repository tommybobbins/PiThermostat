PiThermostat
============


Central heating system and/or Hot water system using a Raspberry Pi and optionally an LCD touchscreen. This project requires at least one TMP102 to make a thermostat. Integrates with Google calendar or Django Schedule to find required temperature. Works with 433MHz sender board to make a complete boiler control system or Shelly relays. Currently works with British Gas and Drayton gas boilers for 433, but Shelly Relays should work for any boiler.

More details about the 433 sender board used can be found https://github.com/tommybobbins/Raspi_433

![](icons/pi_therm_process.png)

The file structure of this project is as follows:
     
    This directory - Python scripts to move to /usr/local/bin
    utilities - useful associated scripts, but may not be required in all cases.
    init - init scripts to be moved to /etc/init.d/
    icons - graphics used by thermostat_gui.py. Can be moved, but icon_dir in thermostat_gui.py will need updating.
    bin - main utilities for running thermostat.
    utilities/433PlanB - to be used in the event of redis/thermostat_gui.py dying.

Requires the Adafruit libraries to read from the TMP102:

    pip install Adafruit_GPIO

Install i2c using raspi-config
 
    sudo raspi-config

Select Advanced mode, enable i2c and then reboot

Most of the Work below can now be performed using make:

    make install

Using django happenings for Calendaring (see Django setup below):

This is now the Default behaviour:

    sudo pip install django-happenings

Install the Python Google API:

     sudo pip install --upgrade google-api-python-client pytz evdev pygame redis smbus configparser
     sudo pip install apiclient urllib3

     mkdir /etc/google_calendar/

Create a new Google calendar called thermostat. You need to allow access through to this calendar here: https://developers.google.com/google-apps/calendar/get_started . Download the client-secrets.json file and put it into /etc/google_calendar/

     sudo cp client-secrets.json /etc/google_calendar

Run the list_calendar.py
     
     cd utilities 
     python list_calendars.py --no_auth_local_webserver

This should create a sample.dat in the local directory. We need to copy this to /etc/google_calendar for neatness.
     
     sudo cp sample.dat /etc/google_calendar

The summary of all events in the calendar should be of the form 

     Temp=20.0

Note that Django-Schedule has supplanted Google Calendar as the default. Uncomment line 88 if you wish to use Google Calendar.

Installation of redis
=====================

     sudo apt-get install redis-server python-redis

Installation of the files
========================

## Setting up a Temperature sensor

This will setup the sensor for the attic.

    cd PiThermostat
    sudo cp utilities/redis_sensor.py /usr/local/bin/
    sudo cp init/redis_sensor.sh /etc/init.d/
    sudo insserv redis_sensor.sh
    sudo cp etc/pithermostat.conf /etc/

Edit /etc/pithermostat.conf to suit

Copy the init script to /etc/init.d/temp.sh

    sudo cp utilities/temp.sh /etc/init.d/
    sudo insserv temp.sh


/etc/hosts should contain the name/location of the redis server:
    
    echo "192.168.1.223     hotf  433board" >>/etc/hosts

To make redis listen on all available ports, edit /etc/redis/redis.conf:

    #bind 127.0.0.1


On the redis server, it is helpful to set a pre-existing weather and optimal temperature (the temperature you want it set to if all else fails):

     pi@raspberrypi ~ $ redis-cli
     redis 127.0.0.1:6379> set temperature/optimal 20
     OK
     redis 127.0.0.1:6379> set temperature/weather 6
     OK

The scripts to copy to /usr/local/bin are as follows:

| Script | Description |
| ------------- | ------------- |
| call_433.py | Makes redis calls to / from the redis server which maintains temperature states/ runs boiler. |
| google_calendar.py | Grabs current temperature required from Google Calendar. |
| processcalendar.py | Deprecated. Was used with django-schedule and is left here for future reference. |
| thermostat_gui.py | Pygame binary to display data on screen and call all other libraries. |
| calculate_temps.py | Pull in the data from the temperature sensors and calculates an internal and external mean |

    sudo cp *.py /usr/local/bin/
    sudo chmod a+rx /usr/local/bin/
    /etc/init.d/temp.sh start

Edit the redis server configuration to allow incoming connections:

    sudo vi /etc/redis/redis.conf

Ensure that it looks like the following:

    # If you want you can bind a single interface, if the bind option is not
    # specified all the interfaces will listen for incoming connections.
    #
    #bind 127.0.0.1

Restart redis:

sudo /etc/init.d/redis-server restart


Using Weather (optional)
========================

Uses weather-util to retrieve weather info:

    sudo apt-get install weather-util

Edit retreive_weather.sh (it is currently set to Leeds/Bradford airport):

    sudo cp utilities/retrieve_weather.sh /usr/local/bin/
    sudo cp utilities/parse_weather.py /usr/local/bin/
    sudo chmod a+x /usr/local/bin/retrieve_weather.sh

    crontab -e
Add a line similar to the following to retrieve the weather for your location

    13 0,6,12,18 * * * /usr/local/bin/retrieve_weather.sh
========================


Setting up the Queue runner on the 433 server
=============================================

All jobs for the 433 transmitter get queued up on a redis server inside jobqueue. This means they can run sequentially stopping the transmitter from garbling two or more messages together. To process this queue, on the 433 sender we need to run a script:

    utilities/read_redis.py

This needs to run as root to get access to the GPIO pin 18 (in our case). It has some protection to only allow 3 binaries to run.  There is an associated init script:

    sudo cp utilities/read_redis.py /usr/local/bin/ 
    sudo cp utilities/murunner.sh /etc/init.d/
    sudo insserv murunner.sh


Django front end
=================

Setting up Django is beyond the scope of this document, but there are instructions on how to do this https://www.djangoproject.com/

    sudo apt-get install -y python-django libapache2-mod-wsgi

Code is inside django. Copy to /usr/local/django and point apache mod_wsgi.conf there. The bottom of the file should look something like:

            WSGIScriptAlias / /usr/local/django/homeauto/wsgi.py
            WSGIPythonPath /usr/local/django
            WSGIPassAuthorization On
    #            <Location />
    #                AuthType Basic
    #                AuthName "Authentication Required"
    #                AuthUserFile "/etc/apache2/htpasswd"
    #                Require valid-user
    #            </Location>


    </IfModule>

Apache should allow the static directories to be served. Add this to /etc/apache/sites-available/default:


        # Non-Django directories
        Alias /static /usr/local/django/homeauto/static/
          <Location "/static">
              SetHandler None
          </Location>

Install the Tango icons:

    sudo pip install django-icons-tango

Create the sqlite database:

    cd /usr/local/django

    sudo python manage.py syncdb

    chmod a+rw home.db

    sudo /etc/init.d/apache2 restart
   
Check that Django Happenings is installed:
 
    sudo pip install django-happenings
