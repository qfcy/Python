# Listing_17-1.py
# Copyright Warren & Carter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Using sprites to put multiple ball images on the screen

import sys, pygame

#-----ball subclass definition -----------------------------
class MyBallClass(pygame.sprite.Sprite):
    def __init__(self, image_file, location):
        pygame.sprite.Sprite.__init__(self)        #call Sprite initializer
        self.image = pygame.image.load(image_file)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location
    
#----- Main Program -----------------------------
size = width, height = 640, 480                          
screen = pygame.display.set_mode(size)                   
screen.fill([255, 255, 255])                             
img_file = "beach_ball.png"
balls = []
for row in range (0, 3):
    for column in range (0, 3):
        location = [column * 180 + 10, row * 180 + 10]
        ball = MyBallClass(img_file, location)
        balls.append(ball)  # Collect the balls in a list
for ball in balls:
    screen.blit(ball.image, ball.rect)
pygame.display.flip()    

running = True    
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
pygame.quit()
