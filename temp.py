#!/usr/bin/python
# touchv5
# Texy 1/6/13

import pygame, sys, os, time
import threading
from pygame.locals import *
import datetime
time.sleep(0)
sys.path.append('/usr/local/lib/python2.7/site-packages/Adafruit-Raspberry-Pi-Python-Code/Adafruit_CharLCDPlate')
from Adafruit_I2C import Adafruit_I2C
import re
import mosquitto
from time import sleep
#from random import choice
poll_time=60
now = time.localtime()
from evdev import InputDevice, list_devices

IDEAL_TEMP=22

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

pygame.init()
# set up the window
#screen = pygame.display.set_mode((320, 240), 0, 32)
#pygame.display.set_caption('Drawing')

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
 
# Fill background
#background = pygame.Surface(screen.get_size())
#background = background.convert()
#background.fill(NAVY_BLUE)




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
    # set up the window
    #screen = pygame.display.set_mode((320, 240), 0, 32)
    #pygame.display.set_caption('Drawing')

    # set up the colors
    #BLACK = (  0,   0,   0)
    #WHITE = (255, 255, 255)
    #RED   = (255,   0,   0)
    #GREEN = (  0, 255,   0)
    #BLUE  = (  0,   0, 255)
    #NAVY_BLUE = ( 0, 0, 192 )
    #CYAN  = (  0, 255, 255)
    #MAGENTA=(255,   0, 255)
    #YELLOW =(255, 255,   0)
 
    now = datetime.datetime.now()
    remaining = int(now.strftime("%S"))
    secs = 60 - remaining
#    print ("Sleeping %i \n" % secs)
    # Fill background
    if ( secs >= 59 ):
        # set up the window
        screen = pygame.display.set_mode((320, 240), 0, 32)
        pygame.display.set_caption('Drawing')
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
	time.sleep(1)
        font = pygame.font.Font(None, 36)
        now = datetime.datetime.now()
        formatted_time = now.strftime("%d-%h-%Y %H:%M")
#        print now.ctime()
        text = font.render("%s" % (formatted_time) , 1, (WHITE))
        temp = font.render("%.2f%sC" % (roundtemp, chr(176)) , 1, (WHITE))
        textpos = text.get_rect(centerx=background.get_width()/2,centery=background.get_height()/2)
        temppos = text.get_rect(centerx=background.get_width()/2,centery=background.get_height()/4)
        temperature_ratio =  floattemp/IDEAL_TEMP
        if ( temperature_ratio >= 1 ):
            background.fill(RED)
        elif ( temperature_ratio <= 1 ):
            background.fill(NAVY_BLUE)
        else:
            background.fill(GREEN)
        print ("%s\n" % temperature_ratio )
        background.blit(text, textpos)
        background.blit(temp, temppos)
        screen.blit(background, (0, 0))
        pygame.display.flip()
        pygame.display.update()
    return

#read_write_temp()

running = True
# run the game loop
while running:
    client.loop()
    read_write_temp()
    for event in pygame.event.get():
        if event.type == QUIT:
            read_write_temp()
            pygame.quit()
            client.disconnect()
            sys.exit()
            running = False  
        elif event.type == pygame.MOUSEBUTTONDOWN:
            print("Pos: %sx%s\n" % pygame.mouse.get_pos())
            read_write_temp()
            if textpos.collidepoint(pygame.mouse.get_pos()):
                pygame.quit()
                client.disconnect()
                sys.exit()
                running = False
        elif event.type == KEYDOWN and event.key == K_ESCAPE:
            running = False
	else:
            read_write_temp()
#    now = datetime.datetime.now()
#    remaining = int(now.strftime("%S"))
#    secs = 60 - remaining
#    print ("Sleeping %i \n" % secs)
#    time.sleep(secs)
