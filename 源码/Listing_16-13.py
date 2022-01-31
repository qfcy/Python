# Listing_16-13.py
# Copyright Warren & Carter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# moving a beach ball image smoothly

import pygame, sys
pygame.init()
screen = pygame.display.set_mode([640,480])
screen.fill([255, 255, 255])
my_ball = pygame.image.load('beach_ball.png')

# start the ball at location [50, 50]
x = 50                                                         
y = 50                                                         
screen.blit(my_ball,[x, y])                           
pygame.display.flip()
for looper in range (1, 100):                                 
    pygame.time.delay(20)         
    
    # erase the ball in its old location, by "painting" white over it                             
    pygame.draw.rect(screen, [255,255,255], [x, y, 90, 90], 0) 
    
    # move the ball horizontally, by changing x 
    x = x + 5
    
    # draw the ball in the new location
    screen.blit(my_ball, [x, y])                       
    pygame.display.flip()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
pygame.quit()
