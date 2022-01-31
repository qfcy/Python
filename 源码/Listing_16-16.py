# Listing_16-16.py
# Copyright Warren & Carter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# move a beach ball image in a pygame window with wrapping

import pygame, sys
pygame.init()
screen = pygame.display.set_mode([640,480])
screen.fill([255, 255, 255])
my_ball = pygame.image.load('beach_ball.png')
x = 50
y = 50
x_speed = 5

running = True    
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            running = False
    pygame.time.delay(20)
    pygame.draw.rect(screen, [255,255,255], [x, y, 90, 90], 0)
    x = x + x_speed
    if x > screen.get_width():        # If the ball is at the far right...                        
        x = 0                         # Start over at the left side                          
    screen.blit(my_ball, [x, y])
    pygame.display.flip()
pygame.quit()

