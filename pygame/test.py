import sys, pygame,math,time
from random import *

__version__='1.1'
class Ball(pygame.sprite.Sprite):
    def __init__(self, image, location, speed,mass=1):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location
        self.pos = location
        self.speed = speed
        self.m = mass

    def move(self):
        self.pos = (self.pos[0]+self.speed[0],self.pos[1]+self.speed[1])
        self.rect.left,self.rect.top = self.pos

        # 检查有无撞到窗口
        if self.rect.left <= 0:
            self.speed[0] = abs(self.speed[0])
        elif self.rect.right >= width:
            self.speed[0] = -abs(self.speed[0])
        if self.rect.top <= 0:
            self.speed[1] = abs(self.speed[1])
        elif self.rect.bottom >= height:
            self.speed[1] = -abs(self.speed[1])
        #else:
            #self.speed[1] += 0.2 # 重力
    def distance(self,other):
        dx=other.rect.left-self.rect.left
        dy=other.rect.top-self.rect.top
        return math.hypot(dx,dy)
    def collide(self,other):
        m1=self.m;m2=other.m
        dx1 = (m1-m2)/(m1+m2)*self.speed[0] + 2*m2/(m2+m1)*other.speed[0]
        dy1 = (m1-m2)/(m1+m2)*self.speed[1] + 2*m2/(m2+m1)*other.speed[1]
        dx2 = (m2-m1)/(m1+m2)*other.speed[0] + 2*m1/(m2+m1)*self.speed[0]
        dy2 = (m2-m1)/(m1+m2)*other.speed[1] + 2*m1/(m2+m1)*self.speed[1]
        self.speed=[dx1, dy1]
        other.speed=[dx2, dy2]

state = {}
def animate(group):
    rect=pygame.rect.Rect((0,0),(width,height))
    screen.fill((255,255,255),rect)
    global ball
    for ball in group:
        ball.move()
    for i in range(len(group)):
        ball=group[i]
        for j in range(i):
            other=group[j]
            collided = ball.distance(other) < ball.rect.width
            # 避免球重复碰撞
            if i!=j:
                if collided and not state.get((i,j),0):
                    ball.collide(other)
                    state[(i,j)] = 1
                elif not collided:
                    state[(i,j)] = 0

        screen.blit(ball.image, ball.rect)
    pygame.display.flip()

#----- Main Program ------------------------------
IMAGESIZE=6
size = width,height = 640, 480
screen = pygame.display.set_mode(size,pygame.RESIZABLE)
screen.fill((255, 255, 255))
image_surface = pygame.surface.Surface((IMAGESIZE, IMAGESIZE))
image_surface.fill((255,255,255))
pygame.draw.circle(image_surface,(140,140,140),(IMAGESIZE//2,IMAGESIZE//2),
                   IMAGESIZE//2)
image = image_surface.convert() 
clock = pygame.time.Clock()
group = []
for row in range(9):
    for column in range(9):
        location = [randrange(width), randrange(height)]
        speed = [random()*8-4, random()*8-4]
        ball = Ball(image,location, speed)
        group.append(ball)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            frame_rate = clock.get_fps()
            print("frame rate = ", frame_rate)
            running = False
        elif event.type == pygame.VIDEORESIZE:
            width,height = event.size
            screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
    animate(group)
    clock.tick(60)
pygame.quit()
