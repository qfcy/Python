# Listing_19-2.py
# Copyright Warren & Carter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Playing music with Pygame

import pygame, sys

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode([640,480])
pygame.time.delay(1000)

pygame.mixer.music.load("bg_music.mp3")  # Load the music file              
pygame.mixer.music.play()                # Play the music

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            running = False
pygame.quit()
