#!/usr/bin/python
# Code based on
# touchv5
# Texy 1/6/13
# Modified 30-Oct-2013
# tng@chegwin.org

import pygame, sys, os, time
import threading
from pygame.locals import *
import datetime
time.sleep(0)
sys.path.append('/usr/local/lib/python2.7/site-packages/Adafruit-Raspberry-Pi-Python-Code/Adafruit_CharLCDPlate')
from Adafruit_I2C import Adafruit_I2C
import re
import fileinput
import mosquitto
from time import sleep
#from random import choice
poll_time=60
now = time.localtime()
from evdev import InputDevice, list_devices

target_temp=22
outside_temp="unknown"
regex = re.compile(r'\s+Temperature:\s+(\d+) F \((\d+) C\)')

#Check to see whether the weather has been downloaded.
try:
   for line in fileinput.input('/tmp/weather_conditions.txt'):
       line = line.rstrip() 
#       print line
       match = regex.search(line)
       if match:
#           print match.group(2)
	   outside_temp= int(match.group(2))
#	   print outside_temp
#       else:
#           print "No match\n"
#           outside_temp="unknown"

except IOError:
   from subprocess import call
   call(["/usr/local/bin/retrieve_weather.sh"])	


client = mosquitto.Mosquitto("Thermo1")
client.connect("mqttserver")

devices = map(InputDevice, list_devices())
eventX=""
for dev in devices:
    if dev.name == "ADS7846 Touchscreen":
        eventX = dev.fn
print eventX

os.environ["SDL_FBDEV"] = "/dev/fb1"
os.environ["SDL_MOUSEDRV"] = "TSLIB"
os.environ["SDL_MOUSEDEV"] = eventX

# set up the window
pygame.init()
iconup = pygame.image.load('icons/OSDChannelUPFO.png')
icondown = pygame.image.load('icons/OSDChannelDownFO.png')

# set up the colors
BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
RED   = (255,   0,   0)
GREEN = (  0, 255,   0)
BLUE  = (  0,   0, 255)
NAVY_BLUE = ( 0, 0, 192 )
CYAN  = (  0, 255, 255)
MAGENTA=(255,   0, 255)
YELLOW =(255, 255,   0)
 
# ============================================================================
# Tmp102 Class
# ============================================================================

class Tmp102:
  i2c = None

  # Constructor
  def __init__(self, address=0x48, mode=1, debug=False):
    self.i2c = Adafruit_I2C(address, debug=debug)

    self.address = address
    self.debug = debug
    # Make sure the specified mode is in the appropriate range
    if ((mode < 0) | (mode > 3)):
      if (self.debug):
        print "Invalid Mode: Using STANDARD by default"
      self.mode = self.__BMP085_STANDARD
    else:
      self.mode = mode

  def readRawTemp(self):
    "Reads the raw (uncompensated) temperature from the sensor"
    self.i2c.write8(0, 0x00)                 # Set temp reading mode
    raw = self.i2c.readList(0,2)

    val = raw[0] << 4;
    val |= raw[1] >> 4;

    return val


  def readTemperature(self):
    "Gets the compensated temperature in degrees celcius"

    RawBytes = self.readRawTemp()  #get the temp from readRawTemp (above)
    temp = float(float(RawBytes) * 0.0625)  #this is the conversion value from the data sheet.
    if (self.debug):
      print "DBG: Raw Temp: 0x%04X (%d)" % (RawBytes & 0xFFFF, RawBytes)
      print "DBG: Calibrated temperature = %f C" % temp
    
    return RawBytes,temp


def read_write_temp():

    now = datetime.datetime.now()
    remaining = int(now.strftime("%S"))
    secs = 60 - remaining
#    print ("Sleeping %i \n" % secs)
    # Fill background
    if ( secs >= 59 ):
        # set up the window
        screen = pygame.display.set_mode((320, 240), 0, 32)
    # Fill background
        background = pygame.Surface(screen.get_size())
        background = background.convert()
        mytemp = Tmp102(address=0x48)
        floattemp = mytemp.readTemperature()[1]
        inttemp =  int(round(floattemp, 22))
        roundtemp =  (round(floattemp, 2))
    # Send temp to MQTT
        client.publish("temperature/sensor", "%f " % floattemp , 1 )
    # Display some text
        font = pygame.font.Font(None, 36)
        now = datetime.datetime.now()
        formatted_time = now.strftime("%d-%h-%Y %H:%M")
#        print now.ctime()
        timefont = pygame.font.Font(None, 24)
        timenow = timefont.render("%s" % (formatted_time) , 1, (WHITE))
        weathernow = timefont.render("Outside: %i%sC" % (outside_temp, chr(176)) , 1, (WHITE))
        idealnow = timefont.render("Target: %i%sC" % (target_temp, chr(176)) , 1, (WHITE))
        temperature_ratio =  floattemp/target_temp
        if ( temperature_ratio >= 1 ):
            fontcolour=RED
        elif ( temperature_ratio <= 1 ):
            fontcolour=BLUE
        else:
	    fontcolour=GREEN
        print ("%s\n" % temperature_ratio )
        tempfont = pygame.font.Font(None, 60)
        temp = tempfont.render("%.2f%sC" % (roundtemp, chr(176)) , 1, (fontcolour))
        timepos = timenow.get_rect(centerx=3*(background.get_width()/4),centery=13*(background.get_height()/14))
        idealpos = idealnow.get_rect(centerx=3*(background.get_width()/4),centery=1*(background.get_height()/14))
        weatherpos = weathernow.get_rect(centerx=1*(background.get_width()/4),centery=13*(background.get_height()/14))
        temppos = temp.get_rect(centerx=90,centery=30)
#        iconup = pygame.image.load('icons/OSDChannelUPFO.png')
#        icondown = pygame.image.load('icons/OSDChannelDownFO.png')
#        print ("%s\n" % temperature_ratio )
        background.fill(BLACK)
#        box = pygame.draw.rect(background,  boxcolor, (0,0,180,60))
        background.blit(timenow, timepos)
        background.blit(temp, temppos)
        background.blit(weathernow, weatherpos)
        background.blit(idealnow, idealpos)
        screen.blit(background, (0, 0))
	screen.blit(iconup,(20,60))
	screen.blit(icondown,(80,60))
        pygame.mouse.set_visible(False)
        pygame.display.flip()
        pygame.display.update()
	sleep(2)
    return

#read_write_temp()

running = True
# run the game loop
while running:
    client.loop()
    read_write_temp()
    for event in pygame.event.get():
#        if event.type == QUIT:
#           read_write_temp()
#            pygame.quit()
#            client.disconnect()
#            sys.exit()
#            running = False  
#        elif event.type == pygame.MOUSEBUTTONDOWN:
#            print("Pos: %sx%s\n" % pygame.mouse.get_pos())
#            read_write_temp()
        pygame.mouse.set_visible(False)
        mos_x, mos_y = pygame.mouse.get_pos()
        print("Pos: %sx%s\n" % pygame.mouse.get_pos())
        if ((mos_x <= 55) and (mos_x > 1)):
            print "mouse is over 'iconup'"
            target_temp+=2
	    read_write_temp()
        elif ((mos_x >= 56) and (mos_x <= 140)):
            print "mouse is over 'icondown'"
            target_temp-=2
	    read_write_temp()
#       elif icondown.get_rect().collidepoint(pygame.mouse.get_pos()):
#           print "mouse is over 'icondown'"
#           pygame.mouse.set_visible(True)
    else:
        print("Pos: %sx%s\n" % pygame.mouse.get_pos())
#           pygame.mouse.set_visible(True)
#            if textpos.collidepoint(pygame.mouse.get_pos()):
#                client.disconnect()
#                 print("Touch: %sx%s\n" % pygame.mouse.get_pos())
#                pygame.quit()
#                sys.exit()
#                running = False
#       elif event.type == KEYDOWN and event.key == K_ESCAPE:
#            running = False
#	else:
#            read_write_temp()
#    now = datetime.datetime.now()
#    remaining = int(now.strftime("%S"))
#    secs = 60 - remaining
#    print ("Sleeping %i \n" % secs)
#    time.sleep(secs)
