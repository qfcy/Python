# Listing_18-4.py
# Copyright Warren & Carter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# First version of PyPong

import pygame, sys                                                        
from pygame.locals import *                                               
  
# Class defintion for the ball
class MyBallClass(pygame.sprite.Sprite):                                  
    def __init__(self, image_file, speed, location):              
        pygame.sprite.Sprite.__init__(self)    
        self.image = pygame.image.load(image_file)                        
        self.rect = self.image.get_rect()                                 
        self.rect.left, self.rect.top = location                          
        self.speed = speed                                                

    def move(self):                                                      
        self.rect = self.rect.move(self.speed)                            
        # bounce off the sides of the window                              
        if self.rect.left < 0 or self.rect.right > screen.get_width():    
            self.speed[0] = -self.speed[0]                                

        # bounce off the top of the window                                
        if self.rect.top <= 0 :                                           
            self.speed[1] = -self.speed[1]                                

# Class definition for the paddle
class MyPaddleClass(pygame.sprite.Sprite):                               
    def __init__(self, location):                                        
        pygame.sprite.Sprite.__init__(self)       
        image_surface = pygame.surface.Surface([100, 20])                
        image_surface.fill([0,0,0])                                      
        self.image = image_surface.convert()
        self.rect = self.image.get_rect()                           
        self.rect.left, self.rect.top = location                         

pygame.init()                                                            
screen = pygame.display.set_mode([640,480])                              
clock = pygame.time.Clock()                                              
myBall = MyBallClass('wackyball.bmp', [10,5], [50, 50])  # make an instance of the ball                
ballGroup = pygame.sprite.Group(myBall)   # add the ball to a sprite group                              
paddle = MyPaddleClass([270, 400])     # make an instance of the paddle                                   

running = True
while running:                                                                 
    clock.tick(30)                                                       
    screen.fill([255, 255, 255])                                         
    for event in pygame.event.get():                                     
        if event.type == QUIT:                                           
            running = False                                                   
        elif event.type == pygame.MOUSEMOTION:     # move the paddle if the                      
            paddle.rect.centerx = event.pos[0]     #   mouse moves                      

    if pygame.sprite.spritecollide(paddle, ballGroup, False):   # bounce the ball if it        
        myBall.speed[1] = -myBall.speed[1]                      #  hits the paddle         
    myBall.move()                                                        
    screen.blit(myBall.image, myBall.rect)                               
    screen.blit(paddle.image, paddle.rect)                               
    pygame.display.flip()
pygame.quit()
