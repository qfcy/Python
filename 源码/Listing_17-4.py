# Listing_17-4.py
# Copyright Warren & Carter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Using Clock and get_fps()

import sys, pygame                                                     
from random import *                                                   

class MyBallClass(pygame.sprite.Sprite):                                
    def __init__(self, image_file, location, speed):   
        pygame.sprite.Sprite.__init__(self)  
        self.image = pygame.image.load(image_file)                      
        self.rect = self.image.get_rect()                               
        self.rect.left, self.rect.top = location                        
        self.speed = speed                                              
  
    def move(self):                                                     
        self.rect = self.rect.move(self.speed)                          
        # check for hitting the side of the window, and if so           
        #  reverse the x-speed                                          
        if self.rect.left < 0 or self.rect.right > width:               
            self.speed[0] = -self.speed[0]                              
   
        # check for hitting the top or bottom of the window, and if so  
        #  reverse the y-speed                                          
        if self.rect.top < 0 or self.rect.bottom > height:              
            self.speed[1] = -self.speed[1]                              
  
def animate(group):                                                    
    screen.fill([255,255,255])                                          
    for ball in group:                                                  
        ball.move()                                                     
    for ball in group:                                                  
        #remove the sprite from the group                               
        group.remove(ball)                                              
  
        #check for collisions between the sprite and the group          
        if pygame.sprite.spritecollide(ball, group, False):             
            ball.speed[0] = -ball.speed[0]                              
            ball.speed[1] = -ball.speed[1]                              
 
        # add the ball back into the group                              
        group.add(ball)                                                 
   
        screen.blit(ball.image, ball.rect)                              
    pygame.display.flip()                                               

#----- Main Program ------------------------------                     
size = width, height = 640, 480                                         
screen = pygame.display.set_mode(size)                                  
screen.fill([255, 255, 255])                                            
img_file = "beach_ball.png"                                             
clock = pygame.time.Clock()                                            
group = pygame.sprite.Group()                                           
for row in range (0, 2):                                                
    for column in range (0, 2):                                         
        location = [column * 180 + 10, row * 180 + 10]                  
        speed = [choice([-4, 4]), choice([-4, 4])]                      
        ball = MyBallClass(img_file, location, speed)                   
        group.add(ball)   #add the ball to the group                    

running = True
while running:                                                                
    for event in pygame.event.get():                                    
        if event.type == pygame.QUIT:                                  
            frame_rate = clock.get_fps()                                
            print "frame rate = ", frame_rate                          
            running = False                                                 
    animate(group)                                                     
    clock.tick(30)
pygame.quit()
