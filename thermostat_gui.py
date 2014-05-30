#!/usr/bin/python
import sys, pygame,operator, os, time
from pygame.locals import *
import time
import pyganim
import redis

redthis = redis.StrictRedis(host='433board',port=6379, db=0, socket_timeout=3)
temperature={}

from evdev import InputDevice, list_devices
devices = map(InputDevice, list_devices())
eventX=""
for dev in devices:
    if dev.name == "ADS7846 Touchscreen":
        eventX = dev.fn
print eventX

os.environ["SDL_FBDEV"] = "/dev/fb1"
os.environ["SDL_MOUSEDRV"] = "TSLIB"
os.environ["SDL_MOUSEDEV"] = eventX

icon_dir='/home/pi/PiThermostat/icons/'
pygame.init()

ball1Anim = pyganim.PygAnimation([(icon_dir+'ball1_360.png', 0.1),
                                 (icon_dir+'ball1_15.png', 0.1),
                                 (icon_dir+'ball1_30.png', 0.1),
                                 (icon_dir+'ball1_45.png', 0.1),
                                 (icon_dir+'ball1_60.png', 0.1),
                                 (icon_dir+'ball1_75.png', 0.1),
                                 (icon_dir+'ball1_90.png', 0.1),
                                 (icon_dir+'ball1_105.png', 0.1),
                                 (icon_dir+'ball1_120.png', 0.1),
                                 (icon_dir+'ball1_135.png', 0.1),
                                 (icon_dir+'ball1_150.png', 0.1),
                                 (icon_dir+'ball1_165.png', 0.1),
                                 (icon_dir+'ball1_180.png', 0.1),
                                 (icon_dir+'ball1_195.png', 0.1),
                                 (icon_dir+'ball1_210.png', 0.1),
                                 (icon_dir+'ball1_225.png', 0.1),
                                 (icon_dir+'ball1_240.png', 0.1),
                                 (icon_dir+'ball1_255.png', 0.1),
                                 (icon_dir+'ball1_270.png', 0.1),
                                 (icon_dir+'ball1_285.png', 0.1),
                                 (icon_dir+'ball1_300.png', 0.1),
                                 (icon_dir+'ball1_315.png', 0.1),
                                 (icon_dir+'ball1_330.png', 0.1),
                                 (icon_dir+'ball1_345.png', 0.1),
                                ])
ball2Anim = pyganim.PygAnimation([(icon_dir+'ball2_360.png', 0.1),
                                 (icon_dir+'ball2_15.png', 0.1),
                                 (icon_dir+'ball2_30.png', 0.1),
                                 (icon_dir+'ball2_45.png', 0.1),
                                 (icon_dir+'ball2_60.png', 0.1),
                                 (icon_dir+'ball2_75.png', 0.1),
                                 (icon_dir+'ball2_90.png', 0.1),
                                 (icon_dir+'ball2_105.png', 0.1),
                                 (icon_dir+'ball2_120.png', 0.1),
                                 (icon_dir+'ball2_135.png', 0.1),
                                 (icon_dir+'ball2_150.png', 0.1),
                                 (icon_dir+'ball2_165.png', 0.1),
                                 (icon_dir+'ball2_180.png', 0.1),
                                 (icon_dir+'ball2_195.png', 0.1),
                                 (icon_dir+'ball2_210.png', 0.1),
                                 (icon_dir+'ball2_225.png', 0.1),
                                 (icon_dir+'ball2_240.png', 0.1),
                                 (icon_dir+'ball2_255.png', 0.1),
                                 (icon_dir+'ball2_270.png', 0.1),
                                 (icon_dir+'ball2_285.png', 0.1),
                                 (icon_dir+'ball2_300.png', 0.1),
                                 (icon_dir+'ball2_315.png', 0.1),
                                 (icon_dir+'ball2_330.png', 0.1),
                                 (icon_dir+'ball2_345.png', 0.1),
                                ])
ball3Anim = pyganim.PygAnimation([(icon_dir+'ball3_360.png', 0.1),
                                 (icon_dir+'ball3_15.png', 0.1),
                                 (icon_dir+'ball3_30.png', 0.1),
                                 (icon_dir+'ball3_45.png', 0.1),
                                 (icon_dir+'ball3_60.png', 0.1),
                                 (icon_dir+'ball3_75.png', 0.1),
                                 (icon_dir+'ball3_90.png', 0.1),
                                 (icon_dir+'ball3_105.png', 0.1),
                                 (icon_dir+'ball3_120.png', 0.1),
                                 (icon_dir+'ball3_135.png', 0.1),
                                 (icon_dir+'ball3_150.png', 0.1),
                                 (icon_dir+'ball3_165.png', 0.1),
                                 (icon_dir+'ball3_180.png', 0.1),
                                 (icon_dir+'ball3_195.png', 0.1),
                                 (icon_dir+'ball3_210.png', 0.1),
                                 (icon_dir+'ball3_225.png', 0.1),
                                 (icon_dir+'ball3_240.png', 0.1),
                                 (icon_dir+'ball3_255.png', 0.1),
                                 (icon_dir+'ball3_270.png', 0.1),
                                 (icon_dir+'ball3_285.png', 0.1),
                                 (icon_dir+'ball3_300.png', 0.1),
                                 (icon_dir+'ball3_315.png', 0.1),
                                 (icon_dir+'ball3_330.png', 0.1),
                                 (icon_dir+'ball3_345.png', 0.1),
                                ])
ball4Anim = pyganim.PygAnimation([(icon_dir+'ball4_360.png', 0.1),
                                 (icon_dir+'ball4_15.png', 0.1),
                                 (icon_dir+'ball4_30.png', 0.1),
                                 (icon_dir+'ball4_45.png', 0.1),
                                 (icon_dir+'ball4_60.png', 0.1),
                                 (icon_dir+'ball4_75.png', 0.1),
                                 (icon_dir+'ball4_90.png', 0.1),
                                 (icon_dir+'ball4_105.png', 0.1),
                                 (icon_dir+'ball4_120.png', 0.1),
                                 (icon_dir+'ball4_135.png', 0.1),
                                 (icon_dir+'ball4_150.png', 0.1),
                                 (icon_dir+'ball4_165.png', 0.1),
                                 (icon_dir+'ball4_180.png', 0.1),
                                 (icon_dir+'ball4_195.png', 0.1),
                                 (icon_dir+'ball4_210.png', 0.1),
                                 (icon_dir+'ball4_225.png', 0.1),
                                 (icon_dir+'ball4_240.png', 0.1),
                                 (icon_dir+'ball4_255.png', 0.1),
                                 (icon_dir+'ball4_270.png', 0.1),
                                 (icon_dir+'ball4_285.png', 0.1),
                                 (icon_dir+'ball4_300.png', 0.1),
                                 (icon_dir+'ball4_315.png', 0.1),
                                 (icon_dir+'ball4_330.png', 0.1),
                                 (icon_dir+'ball4_345.png', 0.1),
                                ])

controlAnim = pyganim.PygAnimation([(icon_dir+'control_360.png', 0.1),
                                 (icon_dir+'control_15.png', 0.1),
                                 (icon_dir+'control_30.png', 0.1),
                                 (icon_dir+'control_45.png', 0.1),
                                 (icon_dir+'control_60.png', 0.1),
                                 (icon_dir+'control_75.png', 0.1),
                                 (icon_dir+'control_90.png', 0.1),
                                 (icon_dir+'control_105.png', 0.1),
                                 (icon_dir+'control_120.png', 0.1),
                                 (icon_dir+'control_135.png', 0.1),
                                 (icon_dir+'control_150.png', 0.1),
                                 (icon_dir+'control_165.png', 0.1),
                                 (icon_dir+'control_180.png', 0.1),
                                 (icon_dir+'control_195.png', 0.1),
                                 (icon_dir+'control_210.png', 0.1),
                                 (icon_dir+'control_225.png', 0.1),
                                 (icon_dir+'control_240.png', 0.1),
                                 (icon_dir+'control_255.png', 0.1),
                                 (icon_dir+'control_270.png', 0.1),
                                 (icon_dir+'control_285.png', 0.1),
                                 (icon_dir+'control_300.png', 0.1),
                                 (icon_dir+'control_315.png', 0.1),
                                 (icon_dir+'control_330.png', 0.1),
                                 (icon_dir+'control_345.png', 0.1),
                                ])

bobAnim = pyganim.PygAnimation([(icon_dir+'bob_pipe1.png', 1.0),
                                 (icon_dir+'bob_pipe2.png', 1.0),
                                 (icon_dir+'bob_pipe3.png', 1.0),
                                 (icon_dir+'bob_pipe4.png', 1.0)])

ball1Anim.play() # there is also a pause() and stop() method
ball2Anim.play() # there is also a pause() and stop() method
ball3Anim.play() # there is also a pause() and stop() method
ball4Anim.play() # there is also a pause() and stop() method
controlAnim.play() # there is also a pause() and stop() method
bobAnim.play() # there is also a pause() and stop() method



#set up the window
screen = pygame.display.set_mode((0, 0), 0, 32)
pygame.mouse.set_visible(False)
icon_dir='/home/pi/PiThermostat/icons/'
mousepos = (200,160)
old_mos_pos=mousepos
screenheight = 320
bob=False
font = pygame.font.SysFont('Arial', 15)
black = 0, 0, 0
shift=(20, -10 )
lowertemp = 15
uppertemp = 25
tempdiff = uppertemp - lowertemp
pixfactor = screenheight/tempdiff
#print ("pixfactor = %f" % pixfactor)
sampling=1000

def convert_temp_to_pixels(temp):
    temp=float(temp)
    y = int(float(screenheight - ((pixfactor)*(temp-lowertemp))))
    return y

def convert_pixels_to_temp(y):
    y = float(screenheight - float(y))
    cont = float((y/pixfactor)+lowertemp)
    shortcont = round(cont,3)
    return (cont,shortcont)

def move_ball(ball,temp,x):
    ballrect = ball.get_rect()
    y = convert_temp_to_pixels(temp)
    ballrect = ballrect.move(x,y)
    if (ball == ball1):
        ball1Anim.blit(screen, (ballrect))
    elif (ball == ball2):
        ball2Anim.blit(screen, (ballrect))
    elif (ball == ball3):
        ball3Anim.blit(screen, (ballrect))
    elif (ball == ball4):
        ball4Anim.blit(screen, (ballrect))
#    screen.blit(ball, ballrect)
    textpos = ballrect.midleft
    textpos = tuple(map(operator.add, textpos,shift))
    screen.blit(font.render('%.0f' % temp, True, (255,255,255)), (textpos))

def move_control(ball,(x,y),control_temp,update_temp):
    (temp,shorttemp)=convert_pixels_to_temp(y)
    control_temp=float(control_temp)
#   Mouse has moved if update_temp is True
    if update_temp:
       try:
#          print ("Mouse moved.Requested temp update to %f" % temp)
          redthis.set("temperature/userrequested",temp)
       except:
          print ("Unable to update requested temperature")
#   Mouse not moved. Lets sanity check against redis
    else:
#        print "We need to check positions"
#        print ("%f, %f" % (temp, control_temp))
        if temp <> control_temp: 
              y=convert_temp_to_pixels(control_temp)
#              print ("Those two not equal new y = %i" % y)
              shorttemp=round(control_temp,3)
              temp = control_temp
#    print ("Moving the globe to y=%i" % y)
##   Finally we can move the control globe to the right position
    ballrect = ball.get_rect()
    ballrect = ballrect.move(x,y)
    screen.blit(ball, ballrect)
    controlAnim.blit(screen, (ballrect))
    textpos = ballrect.midleft
    textpos = tuple(map(operator.add, textpos,shift))
    screen.blit(font.render('%.0f' % shorttemp, True, (255,255,255)), (textpos))
    return temp

def get_temps():    
    # Damocles most likely to be dead (bluetooth), so separate that out
    try:
        d=float(redthis.get("temperature/damocles/sensor"))
    except:
        d=15.0 
    try:
        a=float(redthis.get("temperature/attic/sensor"))
        b=float(redthis.get("temperature/barab/sensor"))
        c=float(redthis.get("temperature/cellar/sensor"))
        control=float(redthis.get("temperature/userrequested"))
        bob=(redthis.get("boiler/req"))
    except:
        a=15.0
        b=15.0
        c=15.0
        control=15.0
        bob=True
    return(a,b,c,d,control,bob)

ball1 = pygame.image.load(icon_dir + "ball1.png")
ball2 = pygame.image.load(icon_dir + "ball2.png")
ball3 = pygame.image.load(icon_dir + "ball3.png")
ball4 = pygame.image.load(icon_dir + "ball4.png")
ball5 = pygame.image.load(icon_dir + "control.png")
while True:
   for event in pygame.event.get():
       if event.type == pygame.QUIT: sys.exit()
       elif event.type == pygame.MOUSEBUTTONDOWN:
            mousepos = pygame.mouse.get_pos()
   screen.fill(black)
   if sampling >= 1000:
       (a,b,c,d,control,bob)=get_temps()
       sampling=0
   move_ball(ball1,a,20)
   move_ball(ball2,b,50)
   move_ball(ball3,c,100)
   move_ball(ball4,d,150)
   if (old_mos_pos <> mousepos):
       control = move_control(ball5,(mousepos),0,True)
#       print(mousepos)
       old_mos_pos = mousepos
   else:
       control = move_control(ball5,(mousepos),control,False)
   if (bob == 'True'):
#      bobview = pygame.image.load(icon_dir + "bob_pipe1.png")
#      bobrect = bobview.get_rect()
#      bobrect = bobrect.move(200,0)
      bobAnim.blit(screen, (200,0))
#      screen.blit(bobview, bobrect)
   pygame.display.flip()
#   print sampling
   sampling +=1

