# Listing_16-7.py
# Copyright Warren & Carter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Drawing curves using a lot of small rectangles

import pygame, sys
import math                                               
pygame.init()
screen = pygame.display.set_mode([640,480])
screen.fill([255, 255, 255])

for x in range(0, 640):                                   
    y = int(math.sin(x/640.0 * 4 * math.pi) * 200 + 240)  # sine wave formula
    
    # draw the wave using small rectangles
    pygame.draw.rect(screen, [0,0,0],[x, y, 1, 1], 1)     # x, y  is the location of each rectangle
                                                          #  in the wave
pygame.display.flip()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            running  = False
pygame.quit()
