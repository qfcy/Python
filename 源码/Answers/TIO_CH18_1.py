# TIO_18-1.py
# Copyright Warren & Carter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Answer to "Try It Out" Question 1 in Chapter 18.
# Final PyPong code, with added feature of fixing 
#  the behaviour when the ball hits the "side" of the paddle 
#  instead of the top.


import pygame, sys   

class MyBallClass(pygame.sprite.Sprite):                                  
    def __init__(self, image_file, speed, location):              
        pygame.sprite.Sprite.__init__(self)  #call Sprite initializer     
        self.image = pygame.image.load(image_file)                        
        self.rect = self.image.get_rect()                                 
        self.rect.left, self.rect.top = location                          
        self.speed = speed                                                
 
    def move(self):                                                       
        global score, score_surf, score_font                                        
        self.rect = self.rect.move(self.speed)                            
        # bounce off the sides of the window                              
        if self.rect.left < 0 or self.rect.right > screen.get_width():    
            self.speed[0] = -self.speed[0]                                

        # bounce off the top of the window                                
        if self.rect.top <= 0 :                                           
            self.speed[1] = -self.speed[1]                                
            score = score + 1
            score_surf = score_font.render(str(score), 1, (0, 0, 0))           
 
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
myBall = MyBallClass('wackyball.bmp', [10,5], [50, 50])                   
ballGroup = pygame.sprite.Group(myBall)                                   
paddle = MyPaddleClass([270, 400])                                        
lives = 3                                                                 
score = 0                                                                
  
score_font = pygame.font.Font(None, 50)
score_surf = score_font.render(str(score), 1, (0, 0, 0))
score_pos = [10, 10]                                                
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
        
        """  
        Check whether the ball is "above" the paddle or "beside" the paddle 
        to know which way to bounce.
                
        Imagine drawing a diagonal line from the topleft corner of the 
        paddle, up and to the left.  If the ball is above this line, it is 
        "above" the paddle, if it is below this line, it is "beside" the paddle.
        Along this line, (y-x) is constant.  Above the line, (y-x) decreases, 
        below the line, (y-x) increases.  So if the ball's (y-x) value is 
        less than the paddle's (y-x) value, the ball is "above" the paddle 
        (so it should bounce up).  If the ball's (y-x) value is greater than the 
        paddle's, it is "beside" the paddle, so it should bounce sideways.  We use the 
        bottom-right corner of the ball and the top-left corner of the paddle to check.

        On the other side, the diagonal line is from the paddle's top-right corner,
        going up and to the right.  In this case, its (y+x) that is constant.  So if 
        the ball's (y+x) is less than the paddle's (y+x), the ball is above (bounces up), 
        and if the ball's (y+x) is greater, it it beside and it bounces sideways.

        The formulas below implement this logic.
        """     
        p_tl_y_min_x = paddle.rect.topleft[1] - paddle.rect.topleft[0]
        p_tr_y_plus_x = paddle.rect.topright[1] + paddle.rect.topright[0]
        b_br_y_min_x = myBall.rect.bottomright[1] - myBall.rect.bottomright[0]
        b_bl_y_plus_x = myBall.rect.bottomleft[1] + myBall.rect.bottomleft[0]
                
        if (b_br_y_min_x > p_tl_y_min_x  or b_bl_y_plus_x > p_tr_y_plus_x):
            # "beside" the paddle, so bounce  x
            myBall.speed[0] = -myBall.speed[0]
        else:
            # "above" the paddle, so bounce y
            myBall.speed[1] = -myBall.speed[1]                                
    myBall.move()                                                         
  
    if not done:                                                          
        screen.blit(myBall.image, myBall.rect)                            
        screen.blit(paddle.image, paddle.rect)                            
        screen.blit(score_surf, score_pos)                                  
        for i in range (lives):                                           
            width = screen.get_width()                                    
            screen.blit(myBall.image, [width - 40 * i, 20])               
        pygame.display.flip()                                             
 
    if myBall.rect.top >= screen.get_rect().bottom:                       
        # lose a life if the ball hits the bottom                         
        lives = lives - 1                                                 
        if lives == 0:                                                    
            final_text1 = "Game Over"                                     
            final_text2 = "Your final score is:  " + str(score)          
            ft1_font = pygame.font.Font(None, 70)                         
            ft1_surf = ft1_font.render(final_text1, 1, (0, 0, 0))             
            ft2_font = pygame.font.Font(None, 50)                         
            ft2_surf = ft2_font.render(final_text2, 1, (0, 0, 0))             
            screen.blit(ft1_surf, [screen.get_width()/2 - \
                        ft1_surf.get_width()/2, 100])
            screen.blit(ft2_surf, [screen.get_width()/2 - \
                        ft2_surf.get_width()/2, 200])
            pygame.display.flip()                                         
            done = True                                                   
        else:  #wait 2 seconds, then start the next ball                  
            pygame.time.delay(2000)                                       
            myBall.rect.topleft = [50, 50]
pygame.quit()
