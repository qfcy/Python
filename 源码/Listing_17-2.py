# Listing 17-2.py
# Copyright Warren & Carter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Moving beach ball images around using sprites

import sys, pygame
from random import *

#-----ball subclass definition -----------------------------
class MyBallClass(pygame.sprite.Sprite):
    def __init__(self, image_file, location, speed):
        pygame.sprite.Sprite.__init__(self)         #call Sprite initializer
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
    
#----- Main Program -----------------------------
size = width, height = 640, 480
screen = pygame.display.set_mode(size)
screen.fill([255, 255, 255])
img_file = "beach_ball.png"
balls = []                                                  
for row in range (0, 3):
    for column in range (0, 3):
        location = [column * 180 + 10, row * 180 + 10]
        speed = [choice([-2, 2]), choice([-2, 2])]        
        ball = MyBallClass(img_file, location, speed)
        balls.append(ball)  # Collect the balls in a list   

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
    pygame.time.delay(20)
    screen.fill([255, 255, 255])                            
    for ball in balls:                                      
            ball.move()                                     
            screen.blit(ball.image, ball.rect)              
    pygame.display.flip()
pygame.quit()
