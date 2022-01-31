# TIO_24_1.py
# Copyright Warren & Carter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Answer to Try It Out, Question 1, Chapter 24

# Lunar Lander with "out of orbit" check

# initialize - get everything ready
import pygame, sys
pygame.init()
screen = pygame.display.set_mode([400,600])
screen.fill([0, 0, 0])
ship = pygame.image.load('lunarlander.png')
moon = pygame.image.load('moonsurface.png')
ground  = 540   #landing pad is y = 540
start = 90
clock = pygame.time.Clock()
ship_mass = 5000.0
fuel = 5000.0
velocity = -100.0
gravity = 10
height = 2000
thrust = 0
delta_v = 0
y_pos = 90
held_down = False

# make the throttle
class ThrottleClass(pygame.sprite.Sprite):
    def __init__(self, location = [0,0]):
        pygame.sprite.Sprite.__init__(self)  #call Sprite initializer
        image_surface = pygame.surface.Surface([30, 10])
        image_surface.fill([128,128,128])
        self.image = image_surface.convert()
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.centery = location

# calcualte position, motion, acceleration, fuel
def calculate_velocity():
    out_of_orbit = False
    global thrust, fuel, velocity, delta_v, height, y_pos
    delta_t = 1/fps
    thrust = (500 - myThrottle.rect.centery) * 5.0  # turn throttle position
                                                     # into amount of thrust 
    fuel -= thrust /(10 * fps)              # use up fuel
    if fuel < 0:  fuel = 0.0
    if fuel < 0.1:  thrust = 0.0
    delta_v = delta_t * (-gravity + 200 * thrust / (ship_mass + fuel))
    velocity = velocity + delta_v
    delta_h = velocity * delta_t
    height = height + delta_h
    y_pos = ground - (height * (ground - start) / 2000) - 90
    # check for velocity or altitude too high - out of orbit
    if velocity > 500 or height > 10000:
        out_of_orbit = True
    return(out_of_orbit)

# display the text with the speed, height, etc.    
def display_stats():
    v_str = "velocity: %i m/s" % velocity
    h_str = "height:   %.1f" % height
    t_str = "thrust:   %i" % thrust
    a_str = "acceleration: %.1f" % (delta_v * fps)
    f_str = "fuel:  %i" % fuel  
    v_font = pygame.font.Font(None, 26)
    v_surf = v_font.render(v_str, 1, (255, 255, 255))
    screen.blit(v_surf, [10, 50])
    a_font = pygame.font.Font(None, 26)
    a_surf = a_font.render(a_str, 1, (255, 255, 255))
    screen.blit(a_surf, [10, 100])
    h_font = pygame.font.Font(None, 26)
    h_surf = h_font.render(h_str, 1, (255, 255, 255))
    screen.blit(h_surf, [10, 150])
    t_font = pygame.font.Font(None, 26)
    t_surf = t_font.render(t_str, 1, (255, 255, 255))
    screen.blit(t_surf, [10, 200])  
    f_font = pygame.font.Font(None, 26)
    f_surf = f_font.render(f_str, 1, (255, 255, 255))
    screen.blit(f_surf, [60, 300])

# display the ship's flames - size depends on the amount of thrust    
def display_flames():
    flame_size = thrust / 15
    for i in range (2):
        startx = 252 - 10 + i * 19
        starty = y_pos + 83
        pygame.draw.polygon(screen, [255, 109, 14], [(startx, starty), 
                                 (startx + 4, starty + flame_size), 
                                 (startx + 8, starty)], 0)

# display final stats when the game is over
def display_final():
    final1 = "Game over"
    final2 = "You landed at %.1f m/s" % velocity
    if velocity > -5:
        final3 = "Nice landing!"
        final4 = "I hear NASA is hiring!"
    elif velocity > -15:
        final3 = "Ouch!  A bit rough, but you survived."
        final4 = "You'll do better next time."
    else:
        final3 = "Yikes!  You crashed a 30 Billion dollar ship."
        final4 = "How are you getting home?"
    pygame.draw.rect(screen, [0, 0, 0], [5, 5, 350, 280],0)  
    f1_font = pygame.font.Font(None, 70)
    f1_surf = f1_font.render(final1, 1, (255, 255, 255))
    screen.blit(f1_surf, [20, 50])   
    f2_font = pygame.font.Font(None, 40)
    f2_surf = f2_font.render(final2, 1, (255, 255, 255))
    screen.blit(f2_surf, [20, 110]) 
    f3_font = pygame.font.Font(None, 26)
    f3_surf = f3_font.render(final3, 1, (255, 255, 255))
    screen.blit(f3_surf, [20, 150]) 
    f4_font = pygame.font.Font(None, 26)
    f4_surf = f4_font.render(final4, 1, (255, 255, 255))
    screen.blit(f4_surf, [20, 180]) 
    pygame.display.flip()
    
# display final stats when the game is over
def display_out_of_orbit():
    final1 = "Out of Orbit"
    final2 = "Game Over"
        
    pygame.draw.rect(screen, [0, 0, 0], [5, 5, 350, 280],0)  
    f1_font = pygame.font.Font(None, 70)
    f1_surf = f1_font.render(final1, 1, (255, 255, 255))
    screen.blit(f1_surf, [20, 50])   
    f2_font = pygame.font.Font(None, 40)
    f2_surf = f2_font.render(final2, 1, (255, 255, 255))
    screen.blit(f2_surf, [20, 110]) 
    pygame.display.flip()

myThrottle = ThrottleClass([15, 500])
out_of_orbit  = False
# main loop
running = True
while running:
    clock.tick(30)
    fps = clock.get_fps()
    if fps < 1:  fps = 30
    if height > 0.01 and not out_of_orbit:    
        out_of_orbit = calculate_velocity()
        screen.fill([0, 0, 0])
        display_stats()
        pygame.draw.rect(screen, [0, 0, 255], [80, 350, 24, 100], 2)
        fuelbar = 96 * fuel / 5000 
        pygame.draw.rect(screen, [0,255,0], [84,448-fuelbar,18, fuelbar], 0) 
        pygame.draw.rect(screen, [255, 0, 0], [25, 300, 10, 200],0) #thrust bar
        screen.blit(moon, [0, 500, 400, 100])                        #moon
        pygame.draw.rect(screen, [60, 60, 60], [220, 535, 70, 5],0) #landing pad
        screen.blit(myThrottle.image, myThrottle.rect)               #thrust handle
        display_flames()                                              #flames
        screen.blit(ship, [230, y_pos, 50, 90])                      #ship
        instructions1 = "Land softly without running out of fuel"
        instructions2 = "Good landing: < 15 m/s    Great landing:  < 5m/s"
        inst1_font = pygame.font.Font(None, 24)
        inst1_surf = inst1_font.render(instructions1, 1, (255, 255, 255))
        screen.blit(inst1_surf, [50, 550])
        inst2_font = pygame.font.Font(None, 24)
        inst2_surf = inst1_font.render(instructions2, 1, (255, 255, 255))
        screen.blit(inst2_surf, [20, 575])
        pygame.display.flip()  
    
    else:  #game over - print final score
        if not out_of_orbit:
            display_final()
        else:
            display_out_of_orbit()
            
                  
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            running  = False
        elif event.type == pygame.MOUSEBUTTONDOWN:          
            held_down = True                                
        elif event.type == pygame.MOUSEBUTTONUP:            
            held_down = False                               
        elif event.type == pygame.MOUSEMOTION:
            if held_down:
                myThrottle.rect.centery = event.pos[1]
                if myThrottle.rect.centery < 300:
                    myThrottle.rect.centery = 300
                if myThrottle.rect.centery > 500:
                    myThrottle.rect.centery = 500
pygame.quit()
