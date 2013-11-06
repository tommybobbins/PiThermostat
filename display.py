#!/usr/bin/python
import pygame
import os
from pygame.locals import *
import gettemperatures
import mosquitto
import time,datetime
import processcalendar
from gettemperatures import read_temps
# Every sample_limit loops we need to re-read our parameters
sample_limit=150
sample=0
fps = 20
working_temp_addition=0
client = mosquitto.Mosquitto("Thermo1")
client.connect("mqttserver")
###########################################################
from evdev import InputDevice, list_devices
devices = map(InputDevice, list_devices())
eventX=""
for dev in devices:
    if dev.name == "ADS7846 Touchscreen":
        eventX = dev.fn
#print eventX

os.environ["SDL_FBDEV"] = "/dev/fb1"
os.environ["SDL_MOUSEDRV"] = "TSLIB"
os.environ["SDL_MOUSEDEV"] = eventX
pygame.init()
###########################################################
screen = pygame.display.set_mode((320, 240), 0, 32)
mainloop =  True
#screen = pygame.display.set_mode((320, 240))
clock = pygame.time.Clock() 
button_up = pygame.image.load('icons/OSDChannelUPFO.png')
button_down = pygame.image.load('icons/OSDChannelDownFO.png')
myFont = pygame.font.SysFont("arial", 30)
button_up_x, button_up_y = 20, 60 
button_down_x, button_down_y = 80, 60 
screen.fill([0,255,0])
screen.blit(button_up, (button_up_x, button_up_y))
screen.blit(button_down, (button_down_x, button_down_y))
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

while mainloop:
    pygame.mouse.set_visible(False)
    tick_time = clock.tick(fps)
    pygame.display.set_caption("Thermostat FPS: %.2f" % (clock.get_fps()))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            mainloop = False
            client.disconnect()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mos_x, mos_y = pygame.mouse.get_pos()
#            print("Pos: %sx%s\n" % pygame.mouse.get_pos())
            if ((mos_x <= 55) and (mos_x > 1)):
#                 print "mouse is over 'iconup'"
                 working_temp_addition += 0.5
#         	 read_write_temp()
#	         pygame.event.clear()
            elif ((mos_x >= 56) and (mos_x <= 140)):
#                 print "mouse is over 'icondown'"
                 working_temp_addition -= 0.5
#                pygame.event.clear()
    if (sample == 0):
#       print "initialising..."
       (floattemp,target_temp,outside_temp) = read_temps() 
       sample += 1
    elif ( sample >= sample_limit):
#       print "attempting to run read_temps"
       old_target_temp=target_temp
       (floattemp,target_temp,outside_temp) = read_temps() 
       client.publish("temperature/sensor", "%f " % floattemp , 1 )
       if (old_target_temp != target_temp ):
           working_temp_addition=0 
       sample = 1 
    elif ( sample <= sample_limit):
       sample += 1
#    print sample
    working_temp=int(target_temp) + working_temp_addition
    roundtemp =  (round(floattemp, 1))
    # Send temp to MQTT
    # Display some text
    font = pygame.font.Font(None, 36)
    now = datetime.datetime.now()
    formatted_time = now.strftime("%d-%h-%Y %H:%M")
    timefont = pygame.font.Font(None, 24)
    timenow = timefont.render("%s" % (formatted_time) , 1, (WHITE))
    weathernow = timefont.render("Outside: %i%sC" % (outside_temp, chr(176)) , 1
, (WHITE))
    idealnow = timefont.render("Target: %.1f%sC" % (working_temp, chr(176)) , 1, (
WHITE))
    temperature_ratio =  floattemp/working_temp
    if ( temperature_ratio >= 1 ):
        fontcolour=RED
    elif ( temperature_ratio <= 1 ):
        fontcolour=BLUE
    else:
        fontcolour=GREEN
#    print ("%s\n" % temperature_ratio )
    tempfont = pygame.font.Font(None, 60)
    temp = tempfont.render("%.1f%sC" % (roundtemp, chr(176)) , 1, (fontcolour))
    timepos = timenow.get_rect(centerx=3*(screen.get_width()/4),centery=13*(screen.get_height()/14))
    idealpos = idealnow.get_rect(centerx=3*(screen.get_width()/4),centery=1*(screen.get_height()/14))
    weatherpos = weathernow.get_rect(centerx=1*(screen.get_width()/4),centery=13*(screen.get_height()/14))
    temppos = temp.get_rect(centerx=90,centery=30)
    screen.fill([0,0,0])
    screen.blit(timenow, timepos)
    screen.blit(temp, temppos)
    screen.blit(weathernow, weatherpos)
    screen.blit(idealnow, idealpos)
    pygame.mouse.set_visible(False)
    screen.blit(button_up, (button_up_x, button_up_y))
    screen.blit(button_down, (button_down_x, button_down_y))
    pygame.display.update()

