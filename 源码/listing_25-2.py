# Listing 25-2
# Copyright Warren & Carter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Building the Skier progrem - obstacles only

import pygame, sys, random
        
# class for obstacle sprites (trees and flags)
class ObstacleClass(pygame.sprite.Sprite):
    def __init__(self, image_file, location, type):
        pygame.sprite.Sprite.__init__(self) 
        self.image_file = image_file        
        self.image = pygame.image.load(image_file)
        self.rect = self.image.get_rect()
        self.rect.center = location
        self.type = type
        self.passed = False
                   
    def update(self):
        global speed
        self.rect.centery -= speed[1]

# create one "screen" of obstacles: 640 x 640
# use "blocks" of 64 x 64 pixels, so objects aren't too close together
def create_map():
    global obstacles
    locations = []
    for i in range(10):                 # 10 obstacles per screen 
        row = random.randint(0, 9)
        col = random.randint(0, 9)
        location  = [col * 64 + 32, row * 64 + 32 + 640] #center x, y for obstacle
        if not (location in locations):        # prevent 2 obstacles in the same place
            locations.append(location)          
            type = random.choice(["tree", "flag"])
            if type == "tree": img = "skier_tree.png"
            elif type == "flag":  img = "skier_flag.png"
            obstacle = ObstacleClass(img, location, type)
            obstacles.add(obstacle)

# redraw the screen, including all sprites
def animate():
    screen.fill([255, 255, 255])
    obstacles.draw(screen)
    pygame.display.flip()    

# initialize everything
pygame.init()
screen = pygame.display.set_mode([640,640])
clock = pygame.time.Clock()
speed = [0, 6]
obstacles = pygame.sprite.Group()
map_position = 0
create_map()

# main Pygame event loop
running = True
while running:
    clock.tick(30)
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        
    map_position += speed[1]                      # scroll the obstacles
    
    # create a new block of obstacles at the bottom
    if map_position >= 640:
        create_map()
        map_position = 0
    
    obstacles.update()
    animate()
    
pygame.quit()
    
