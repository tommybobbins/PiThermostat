#!/usr/bin/python
# touchv5
# Texy 1/6/13

import pygame, sys, os, time
from pygame.locals import *

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

pygame.init()

# set up the window
screen = pygame.display.set_mode((320, 240), 0, 32)
pygame.display.set_caption('Drawing')

# set up the colors
BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
RED   = (255,   0,   0)
GREEN = (  0, 255,   0)
BLUE  = (  0,   0, 255)
CYAN  = (  0, 255, 255)
MAGENTA=(255,   0, 255)
YELLOW =(255, 255,   0)
 
# Fill background
background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill(WHITE)
box = pygame.draw.rect(background, YELLOW,(0, 0, 40, 240))
box = pygame.draw.rect(background,  CYAN, (40, 0, 40, 240))
box = pygame.draw.rect(background, GREEN, (80, 0, 40, 240))
box = pygame.draw.rect(background,MAGENTA,(120, 0, 40, 240))
box = pygame.draw.rect(background, RED,   (160, 0, 40, 240))
box = pygame.draw.rect(background, BLUE  ,(200, 0, 40, 240))
box = pygame.draw.rect(background, BLACK ,(240, 0, 40, 240))

# Display some text
font = pygame.font.Font(None, 36)
text = font.render("Touch here", 1, (BLACK))
#text = pygame.transform.rotate(text,270) 
textpos = text.get_rect(centerx=background.get_width()/2,centery=background.get_height()/2)
background.blit(text, textpos)

screen.blit(background, (0, 0))
pygame.display.flip()

running = True
# run the game loop
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
            running = False  
        elif event.type == pygame.MOUSEBUTTONDOWN:
            print("Pos: %sx%s\n" % pygame.mouse.get_pos())
            if textpos.collidepoint(pygame.mouse.get_pos()):
                pygame.quit()
                sys.exit()
                running = False
        elif event.type == KEYDOWN and event.key == K_ESCAPE:
            running = False
    pygame.display.update()

