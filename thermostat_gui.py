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

bobAnim = pyganim.PygAnimation([(icon_dir+'bob_pipe1.png', 1.0),
                                 (icon_dir+'bob_pipe2.png', 1.0),
                                 (icon_dir+'bob_pipe3.png', 1.0),
                                 (icon_dir+'bob_pipe4.png', 1.0)])

bobAnim.play() # there is also a pause() and stop() method



#set up the window
screen = pygame.display.set_mode((0, 0), 0, 32)
pygame.mouse.set_visible(False)
icon_dir='/home/pi/PiThermostat/icons/'
mousepos = (200,160)
old_mos_pos=mousepos
screenheight = 320
bob=False
font = pygame.font.SysFont('Arial', 12)
black = 0, 0, 0
shift=(25, 35 )
circleshift=(7, 7 )
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
    screen.blit(ball, ballrect)
    textpos = ballrect.midleft
    textpos = tuple(map(operator.add, textpos,shift))
    circlepos = tuple(map(operator.add, textpos,circleshift))
    pygame.draw.circle(screen,(255,255,255), circlepos, 10, 1)
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
    textpos = ballrect.midleft
    textpos = tuple(map(operator.add, textpos,shift))
    circlepos = tuple(map(operator.add, textpos,circleshift))
    pygame.draw.circle(screen,(255,255,255), circlepos, 10, 1)
    screen.blit(font.render('%.0f' % shorttemp, True, (255,255,255)), (textpos))
    pygame.time.wait(40)
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
   pygame.time.wait(40)
#   print sampling
   sampling +=1

