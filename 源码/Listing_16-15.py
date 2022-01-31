# Listing_16-15.py
# Copyright Warren & Carter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Bounce a beach ball in 2-D in a pygame window

import pygame, sys
pygame.init()
screen = pygame.display.set_mode([640,480])
screen.fill([255, 255, 255])
my_ball = pygame.image.load('beach_ball.png')
x = 50
y = 50
x_speed = 10                             # now we have both x_speed
y_speed = 10                             #  and y_speed

running = True    
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            running = False
    
    pygame.time.delay(20)
    pygame.draw.rect(screen, [255,255,255], [x, y, 90, 90], 0)  
    x = x + x_speed                                 # move the ball hirizontally
    y = y + y_speed                                 #  and vertically              
    if x > screen.get_width() - 90  or  x < 0:      # bounce off the sides
        x_speed = - x_speed
    if y > screen.get_height() - 90 or y < 0:       # bounce off the top, bottom              
        y_speed = -y_speed                                        
    screen.blit(my_ball, [x, y])
    pygame.display.flip()

pygame.quit()
