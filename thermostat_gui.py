#!/usr/bin/python
import pygame, os, subprocess, sys
from pygame.locals import *
import gettemperatures, call_433, time, datetime, processcalendar
from gettemperatures import read_temps
from call_433 import publish_redis
from call_433 import send_boiler 
# Every sample_limit loops we need to re-read our parameters
sample_limit=150
sample=0
fps = 4 
target_temp=14
boiler_request_time=20 # Seconds
last_boiler_req=False
working_temp_addition=0
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
button_up_unlit = pygame.image.load('/home/pi/PiThermostat/icons/OSDChannelUpNF.png')
button_up_lit = pygame.image.load('/home/pi/PiThermostat/icons/OSDChannelUpFO.png')
button_down_unlit = pygame.image.load('/home/pi/PiThermostat/icons/OSDChannelDownNF.png')
button_down_lit = pygame.image.load('/home/pi/PiThermostat/icons/OSDChannelDownFO.png')
myFont = pygame.font.SysFont("arial", 30)
button_up_x, button_up_y = 20, 60 
button_down_x, button_down_y = 120, 60 
screen.fill([0,255,0])
screen.blit(button_up_unlit, (button_up_x, button_up_y))
screen.blit(button_down_unlit, (button_down_x, button_down_y))
# set up the colors
BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
RED   = (255,   0,   0)
GREEN = (  0, 255,   0)
BLUE  = (  0,   0, 255)
NAVY_BLUE = ( 0, 0, 192 )
PURPLE = ( 192, 0, 192 )
CYAN  = (  0, 255, 255)
MAGENTA=(255,   0, 255)
YELLOW =(204, 204,   240)

def screenupdate(time,temp,weather,ideal,tempcolour):

#    print ("Weather = %i" % weather)
    tempfont = pygame.font.Font(None, 60)
    tempnow = tempfont.render("%.1f%sC" % (temp, chr(176)) , 1, (tempcolour))
    timepos = timenow.get_rect(centerx=3*(screen.get_width()/4),centery=13*(screen.get_height()/14))
    idealpos = idealnow.get_rect(centerx=3*(screen.get_width()/4),centery=1*(screen.get_height()/14))
    weatherpos = weathernow.get_rect(centerx=1*(screen.get_width()/4),centery=13*(screen.get_height()/14))
    temppos = tempnow.get_rect(centerx=90,centery=30)
    screen.fill([0,0,0])
    screen.blit(timenow, timepos)
    screen.blit(tempnow, temppos)
    screen.blit(weathernow, weatherpos)
    screen.blit(idealnow, idealpos)
    pygame.mouse.set_visible(False)
    screen.blit(button_up_unlit, (button_up_x, button_up_y))
    screen.blit(button_down_unlit, (button_down_x, button_down_y))
    pygame.display.update()


while mainloop:
    from subprocess import call
    need_to_update=0
    pygame.mouse.set_visible(False)
    tick_time = clock.tick(fps)
    pygame.display.set_caption("Thermostat FPS: %.2f" % (clock.get_fps()))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            mainloop = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mos_x, mos_y = pygame.mouse.get_pos()
#            print("Pos: %sx%s\n" % pygame.mouse.get_pos())
            if ((mos_x <= 100) and (mos_x > 1)):
                  #Mouse if over icon Up
		  #sudo switch_on_off_backlight.sh on
		  subprocess.call(["/usr/local/bin/switch_on_off_backlight.sh","on"])
                  screen.blit(button_up_lit, (button_up_x, button_up_y))
                  need_to_update=1
                  working_temp_addition += 0.5
                  pygame.display.update()
            elif ((mos_x >= 101) and (mos_x <= 220)):
                  #Mouse if over icon Down
		  #sudo switch_on_off_backlight.sh on
		  subprocess.call(["/usr/local/bin/switch_on_off_backlight.sh","on"])
                  screen.blit(button_down_lit, (button_down_x, button_down_y))
                  need_to_update=1
                  working_temp_addition -= 0.5
                  pygame.display.update()
####### If we are running for the first time
    if (sample == 0):
       (floattemp,target_temp,outside_temp) = read_temps() 
#       print ("Outside temp = %i " % outside_temp)
       boiler_request_time=20 # Seconds
       sample += 1
       need_to_update=1
####### If we are doing our regular update
    elif ( sample >= sample_limit):
#       print "attempting to run read_temps"
       old_target_temp=target_temp
       (floattemp,target_temp,outside_temp) = read_temps() 
       print ("Outside temp = %i " % outside_temp)
       need_to_update=1
       boiler_request_time=295 # Seconds
       if (old_target_temp != target_temp ):
           working_temp_addition=0 
       sample = 1 
####### If we are doing our regular update just increment the sample
    elif ( sample <= sample_limit):
       sample += 1
###########################################
    working_temp = target_temp + working_temp_addition
    roundtemp =  (round(floattemp, 1))
    # Display some text
    font = pygame.font.Font(None, 36)
    now = datetime.datetime.now()
    formatted_time = now.strftime("%d-%h-%Y %H:%M")
    timefont = pygame.font.Font(None, 24)
    timenow = timefont.render("%s" % (formatted_time) , 1, (YELLOW))
    weathernow = timefont.render("Outside: %i%sC" % (outside_temp, chr(176)) , 1, (WHITE))
    idealnow = timefont.render("Target: %.1f%sC" % (working_temp, chr(176)) , 1, (WHITE))
    temperature_ratio =  floattemp/working_temp
    if ( temperature_ratio >= 1 and temperature_ratio <= 1.025 ):
        fontcolour=GREEN
        boiler_req=True
    elif ( temperature_ratio <= 1 ):
        fontcolour=BLUE
        boiler_req=True
    elif ( temperature_ratio >= 1.025 ):
        fontcolour=RED
        boiler_req=False
    else:
        fontcolour=PURPLE
        boiler_req=False
#    print ("%s\n" % temperature_ratio )
#    tempfont = pygame.font.Font(None, 60)
#    tempnow = tempfont.render("%.1f%sC" % (roundtemp, chr(176)) , 1, (fontcolour))
#    timepos = timenow.get_rect(centerx=3*(screen.get_width()/4),centery=13*(screen.get_height()/14))
#    idealpos = idealnow.get_rect(centerx=3*(screen.get_width()/4),centery=1*(screen.get_height()/14))
#    weatherpos = weathernow.get_rect(centerx=1*(screen.get_width()/4),centery=13*(screen.get_height()/14))
#    temppos = tempnow.get_rect(centerx=90,centery=30)
    if (need_to_update == 1):
#       print ("screen update")
#       print ("sample = %i" % sample)
#       Assume sample_limit is set to 150 @ 4 fps, will be called every 37.5s
       screenupdate(timenow,roundtemp, weathernow, idealnow,fontcolour)
       try:
           publish_redis(floattemp, working_temp)
           send_boiler(boiler_req, boiler_request_time)
       except:
           print "Publishing error:", sys.exc_info()[0]
#           print "Unable to publish"
       need_to_update = 0
       
