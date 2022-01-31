# Listing_19-3.py
# Copyright Warren & Carter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Music and sound with volume adjustment

import pygame, sys
pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode([640,480])
pygame.time.delay(1000)

pygame.mixer.music.load("bg_music.mp3")
pygame.mixer.music.set_volume(0.3)         # Adjust the volume on the music
pygame.mixer.music.play()
splat = pygame.mixer.Sound("splat.wav")    # Adjust the volume on the "splat" sound
splat.set_volume(0.5) 
splat.play()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            running = False
pygame.quit()
