# Listing_16-2.py
# Copyright Warren & Carter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Making the Pygame window work properly

import pygame
pygame.init()
screen = pygame.display.set_mode([640, 480])
running  = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
pygame.quit()

