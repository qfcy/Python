# Listing_16-4.py
# Copyright Warren & Carter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Draw a circle in the middle of the window

import pygame, sys
pygame.init()
screen = pygame.display.set_mode([640,480])
screen.fill([255, 255, 255])

# draw circle in the middle of the Pygame window
pygame.draw.circle(screen, [255,0,0],[320,240], 30, 0)    # [320,240] is the new location   
pygame.display.flip()
running  = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            running = False
pygame.quit()
