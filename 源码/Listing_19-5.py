# Listing_19-5.py
# Copyright Warren & Csrter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# PyPong with sounds and music

import pygame, sys 
 
class MyBallClass(pygame.sprite.Sprite): 
    def __init__(self, image_file, speed, location = [0,0]): 
        pygame.sprite.Sprite.__init__(self)   
        self.image = pygame.image.load(image_file) 
        self.rect = self.image.get_rect() 
        self.rect.left, self.rect.top = location 
        self.speed = speed 
 
    def move(self): 
        global points, score_text 
        self.rect = self.rect.move(self.speed) 
        if self.rect.left < 0 or self.rect.right > screen.get_width():
            self.speed[0] = -self.speed[0] 
            if self.rect.top < screen.get_height(): 
                hit_wall.play()          #Play sound when the ball hits the side wall
                                               
        if self.rect.top <= 0 : 
            self.speed[1] = -self.speed[1] 
            points = points + 1 
            score_text = font.render(str(points), 1, (0, 0, 0)) 
            get_point.play()             #Plays sound when the ball hits the top
                                         #   (player gets a point)

class MyPaddleClass(pygame.sprite.Sprite): 
    def __init__(self, location = [0,0]): 
        pygame.sprite.Sprite.__init__(self) 
        image_surface = pygame.surface.Surface([100, 20]) 
        image_surface.fill([0,0,0]) 
        self.image    = image_surface.convert() 
        self.rect = self.image.get_rect() 
        self.rect.left, self.rect.top = location 
pygame.init()
pygame.mixer.init()


pygame.mixer.music.load("bg_music.mp3")          # Load background music
pygame.mixer.music.set_volume(0.3)               # Set volume for music
pygame.mixer.music.play(-1)                      # Play music forever
hit = pygame.mixer.Sound("hit_paddle.wav")          # Load other sounds 
hit.set_volume(0.4)                                 #   and set their volumes 
new_life = pygame.mixer.Sound("new_life.wav")       #
new_life.set_volume(0.5)                            #
splat = pygame.mixer.Sound("splat.wav")             #
splat.set_volume(0.6)                               #
hit_wall = pygame.mixer.Sound("hit_wall.wav")       #
hit_wall.set_volume(0.4)                            #
get_point = pygame.mixer.Sound("get_point.wav")     #
get_point.set_volume(0.2)                           #
bye = pygame.mixer.Sound("game_over.wav")           #
bye.set_volume(0.6)                                 #

screen = pygame.display.set_mode([640,480]) 
clock = pygame.time.Clock() 

myBall = MyBallClass('wackyball.bmp', [12,6], [50, 50]) 
ballGroup = pygame.sprite.Group(myBall) 
paddle = MyPaddleClass([270, 400]) 
lives = 3 
points = 0 
 
font = pygame.font.Font(None, 50) 
score_text = font.render(str(points), 1, (0, 0, 0)) 
textpos = [10, 10] 
done = False 

running = True 
while running: 
    clock.tick(30) 
    screen.fill([255, 255, 255]) 
    for event in pygame.event.get(): 
        if event.type == pygame.QUIT: 
            running = False 
        elif event.type == pygame.MOUSEMOTION: 
            paddle.rect.centerx = event.pos[0] 
 
    if pygame.sprite.spritecollide(paddle, ballGroup, False): 
        hit.play()                              # Play sound when the ball hits the paddle
        myBall.speed[1] = -myBall.speed[1] 
 
    myBall.move() 
 
    if not done: 
        screen.blit(myBall.image, myBall.rect) 
        screen.blit(paddle.image, paddle.rect) 
        screen.blit(score_text, textpos) 
        for i in range (lives): 
            width = screen.get_width() 
            screen.blit(myBall.image, [width - 40 * i, 20]) 
        pygame.display.flip() 
 
    if myBall.rect.top >= screen.get_rect().bottom: 
        if not done: 
            splat.play()           # Plays sound when the player loses a life
        lives = lives - 1 
        if lives <= 0: 
            if not done: 
                pygame.time.delay(1000)             #Wait one second, 
                bye.play()                          #  then play the ending sound
            final_text1 = "Game Over" 
            final_text2 = "Your final score is:  " + str(points) 
            ft1_font = pygame.font.Font(None, 70) 
            ft1_surf = font.render(final_text1, 1, (0, 0, 0)) 
            ft2_font = pygame.font.Font(None, 50) 

            ft2_surf = font.render(final_text2, 1, (0, 0, 0)) 
            screen.blit(ft1_surf, [screen.get_width()/2 - \
                        ft1_surf.get_width()/2, 100]) 
            screen.blit(ft2_surf, [screen.get_width()/2 - \
                        ft2_surf.get_width()/2, 200]) 

            pygame.display.flip() 
            done = True 
            pygame.mixer.music.fadeout(2000)        #Fade out the music
        else: 
            pygame.time.delay(1000)                 
            new_life.play()                         #Play sound when a new life starts
            myBall.rect.topleft = [50, 50] 
            screen.blit(myBall.image, myBall.rect) 
            pygame.display.flip() 
            pygame.time.delay(1000)
pygame.quit()
