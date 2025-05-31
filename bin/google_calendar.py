#!/usr/bin/python3
# Modified 27-Sep-2015
# tng@chegwin.org

# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Command-line skeleton application for Calendar API.
Usage:
  $ python sample.py

You can also get help on all the command-line flags the program understands
by running:

  $ python sample.py --help

"""

import argparse
import httplib2
import os
import sys
import pytz
import re
import redis
import configparser
import sys
sys.path.append('/usr/local/python/lib')
from pithermostat.logging_helper import debug_log, info_log, error_log, warning_log
regex_temp = re.compile(r'^Temp=(.*)')
from datetime import datetime, timedelta

from apiclient import discovery
from oauth2client import file
from oauth2client import client
from oauth2client import tools

# Parser for command-line arguments.
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[tools.argparser])


# CLIENT_SECRETS is name of a file containing the OAuth 2.0 information for this
# application, including client_id and client_secret. You can see the Client ID
# and Client secret on the APIs page in the Cloud Console:
CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), '/etc/google_calendar/client_secrets.json')

# Set up a Flow object to be used for authentication.
# Add one or more of the following scopes. PLEASE ONLY ADD THE SCOPES YOU
# NEED. For more information on using scopes please see
# <https://developers.google.com/+/best-practices>.
FLOW = client.flow_from_clientsecrets(CLIENT_SECRETS,
  scope=[
      'https://www.googleapis.com/auth/calendar',
      'https://www.googleapis.com/auth/calendar.readonly',
    ],
    message=tools.message_if_missing(CLIENT_SECRETS))

parser = configparser.ConfigParser()
parser.read('/etc/pithermostat.conf')

redishost=parser.get('redis','broker')
redisport=int(parser.get('redis','port'))
redisdb=parser.get('redis','db')
redistimeout=float(parser.get('redis','timeout'))
redthis=redis.StrictRedis(host=redishost,port=redisport, db=redisdb, socket_timeout=redistimeout)

def process_google_calendar():
    try:
        debug_log("Processing Google Calendar")
        # If the credentials don't exist or are invalid run through the native client
        # flow. The Storage object will ensure that if successful the good
        # credentials will get written back to the file.
        storage = file.Storage('/etc/google_calendar/sample.dat')
        credentials = storage.get()
        return_temp = 13.6654
        if credentials is None or credentials.invalid:
            credentials = tools.run_flow(FLOW, storage, flags)

        # Create an httplib2.Http object to handle our HTTP requests and authorize it
        # with our good Credentials.
        http = httplib2.Http()
        http = credentials.authorize(http)

        # Construct the service object for the interacting with the Calendar API.
        service = discovery.build('calendar', 'v3', http=http)

        baildon_tz = pytz.timezone('Europe/London')
        now = datetime.now(tz=baildon_tz) # timezone?
        timeMin = baildon_tz.localize(datetime(year=now.year, month=now.month, day=now.day, hour=now.hour, minute=now.minute, second=now.second ))
        timeMin = timeMin.isoformat()
        timeMax = baildon_tz.localize(datetime(year=now.year, month=now.month, day=now.day, hour=now.hour, minute=now.minute, second=now.second ) + timedelta(minutes=1))
        timeMax = timeMax.isoformat()
        page_token = None
        while True:
            # Replace thermostat with
            #  <something>@group.calendar.google.com
            # where something is found from running 
            # PiThermostat/utilities/list_calendars.py
            events = service.events().list(calendarId='thermostat',timeMin=timeMin, timeMax=timeMax).execute()
            for event in events['items']:
                tempstring = event['summary']
                match = regex_temp.search(tempstring)
                if match:
                    target_temp = float(match.group(1))
                    return_temp = target_temp
                else:
                    return_temp = 13.6654
            page_token = events.get('nextPageToken')
            if not page_token:
                break
        return return_temp

    except Exception as e:
        error_log(f"Error processing Google Calendar: {str(e)}")
        raise

# For more information on the Calendar API you can visit:
#
#   https://developers.google.com/google-apps/calendar/firstapp
#
# For more information on the Calendar API Python library surface you
# can visit:
#
#   https://developers.google.com/resources/api-libraries/documentation/calendar/v3/python/latest/
#
# For information on the Python Client Library visit:
#
#   https://developers.google.com/api-client-library/python/start/get_started

if __name__ == "__main__":
    try:
        process_google_calendar()
    except Exception as e:
        error_log(f"Fatal error: {str(e)}")
        sys.exit(1)
