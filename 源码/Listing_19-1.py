# Listing_19-1.py
# Copyright Warren & Carter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Trying out sounds in Pygame

import pygame
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode([640,480])
pygame.time.delay(1000)    # Wait a second for the mixer to finish initializing

splat = pygame.mixer.Sound("splat.wav")   # Create the Sound object
splat.play()                              # Play the sound

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            running = False
pygame.quit()
