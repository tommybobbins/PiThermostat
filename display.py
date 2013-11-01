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
import mosquitto
import gettemperatures
from gettemperatures import read_temps
from time import sleep
#from random import choice
poll_time=60
working_temp=21
now = time.localtime()
from evdev import InputDevice, list_devices

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
 
def do_display():

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
        (floattemp,target_temp,outside_temp) = read_temps() 
	working_temp=target_temp
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
        idealnow = timefont.render("Target: %i%sC" % (working_temp, chr(176)) , 1, (WHITE))
        temperature_ratio =  floattemp/working_temp
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
#	sleep(2)
        return

running = True
# run the game loop
while running:
    client.loop()
    target_temp=do_display()
    for event in pygame.event.get():
        pygame.mouse.set_visible(False)
        mos_x, mos_y = pygame.mouse.get_pos()
        print("Pos: %sx%s\n" % pygame.mouse.get_pos())
        if ((mos_x <= 55) and (mos_x > 1)):
            print "mouse is over 'iconup'"
            working_temp += 2
#	    read_write_temp()
        elif ((mos_x >= 56) and (mos_x <= 140)):
            print "mouse is over 'icondown'"
            working_temp -= 2
    else:
        print("Pos: %sx%s\n" % pygame.mouse.get_pos())
