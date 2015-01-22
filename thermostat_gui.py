#!/usr/bin/python
import sys, pygame,operator, os, time
from pygame.locals import *
import random
import math
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
TARGET_FPS=6
clock = pygame.time.Clock()
black = 0, 0, 0
shift=(-5, 35 )
circleshift=(7, 7)
revcircleshift=(-7, -7)
jiggle=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,-1]
lowertemp = 15
uppertemp = 25
tempdiff = uppertemp - lowertemp
pixfactor = screenheight/tempdiff
#print ("pixfactor = %f" % pixfactor)
#number_positions=500
#angle_to_move = ((2*math.pi)/number_positions)
#globe_radius=50
#ball1angle=random.uniform(0,2*math.pi)
#ball2angle=random.uniform(0,2*math.pi)
#ball3angle=random.uniform(0,2*math.pi)
#ball4angle=random.uniform(0,2*math.pi)
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
#    calc_angle = current_angle + angle_to_move
#    if (calc_angle  >= (2 * math.pi)):
#        calc_angle=0
    ballrect = ball.get_rect()
#    shift=(int(globe_radius*math.cos(calc_angle)), int(globe_radius*math.sin(calc_angle)))
#    print shift
    x = int(x)
    y = int(convert_temp_to_pixels(temp))
    random_jiggle=(random.choice(jiggle),random.choice(jiggle))
#    print random_jiggle
    (x,y) = tuple(map(operator.add, (x,y),random_jiggle))
    ballrect = ballrect.move(x,y)
#    print (x,y)
    screen.blit(ball, ballrect)
    #ballrect = ball.get_rect()
    textpos = ballrect.center
    textpos = tuple(map(operator.add, textpos,shift))
#    textpos = tuple(map(operator.add, textpos,revcircleshift))
    textpos = tuple(map(operator.add, textpos,random_jiggle))
    circlepos = tuple(map(operator.add, textpos,circleshift))
    pygame.draw.circle(screen,(255,255,255), circlepos, 10, 1)
#    print circlepos
    screen.blit(font.render('%.0f' % temp, True, (255,255,255)), (textpos))
#    return calc_angle
    pygame.time.wait(40)

def move_control(ball,(x,y),control_temp,update_temp):
    (temp,shorttemp)=convert_pixels_to_temp(y)
    control_temp=float(control_temp)
    ballrect = ball.get_rect()
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
    ballrect = ballrect.move(x,y)
    screen.blit(ball, ballrect)
    textpos = ballrect.center
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
    except:
        a=15.0
    try:
        b=float(redthis.get("temperature/barab/sensor"))
    except:
        b=15.0
    try:
        c=float(redthis.get("temperature/cellar/sensor"))
    except:
        c=15.0
    try:
        control=float(redthis.get("temperature/userrequested"))
    except:
        control=15.0
    try:
        bob=(redthis.get("boiler/req"))
    except:
        bob=True
#    print(a,b,c,d,control,bob)
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
   if sampling >= 100:
       (a,b,c,d,control,bob)=get_temps()
       sampling=0
   ball1rect=ball1.get_rect()
   ball2rect=ball2.get_rect()
   ball3rect=ball3.get_rect()
   ball4rect=ball4.get_rect()
   if ball1rect.colliderect(ball2rect):
      move_ball(ball1,a,15)
      move_ball(ball2,b,55)
   else:
      move_ball(ball1,a,20)
      move_ball(ball2,b,50)
   if ball2rect.colliderect(ball3rect):
      move_ball(ball3,c,105)
   else:
      move_ball(ball3,c,100)
   if ball3rect.colliderect(ball4rect):
      move_ball(ball4,d,150)
   else:
      move_ball(ball4,d,150)
#   print angle
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
   clock.tick(TARGET_FPS)
#   print sampling
   sampling +=1

