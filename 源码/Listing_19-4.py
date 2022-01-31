# Listing_19-4.py
# Copyright Warren & Carter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Waiting for the end of the song.

import pygame, sys
pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode([640,480])
pygame.time.delay(1000)

pygame.mixer.music.load("bg_music.mp3")
pygame.mixer.music.set_volume(0.3) 
pygame.mixer.music.play(2)
splat = pygame.mixer.Sound("splat.wav")
splat.set_volume(0.5) 

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            running = False

    if not pygame.mixer.music.get_busy():   # Check if the music is done playing
        splat.play()                        # Play the "splat" sound
        pygame.time.delay(1000)             # Wait a second for the splat sound to finish
        running = False

pygame.quit()
