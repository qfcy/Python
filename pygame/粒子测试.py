import sys, pygame,math,time
from random import *

__version__='1.1'
class Vec2D(list): # 基于turtle模块的Vec2D修改
    """A 2 dimensional vector class, used as a helper class
    for implementing turtle graphics.
    May be useful for turtle graphics programs also.
    Derived from list, so a vector is a list!
    """
    def __init__(self,*args):
        if len(args)==1:
            list.__init__(self,args[0])
        else:
            list.__init__(self,args)
    def __add__(self, other):
        return Vec2D(self[0] + other[0], self[1] + other[1])
    def __mul__(self, other):
        if isinstance(other, Vec2D):
            return self[0] * other[0] + self[1] * other[1]
        return Vec2D(self[0] * other, self[1] * other)

    def __rmul__(self, other):
        if isinstance(other, (int, float)):
            return Vec2D(self[0] * other, self[1] * other)

    def __sub__(self, other):
        return Vec2D(self[0] - other[0], self[1] - other[1])

    def __neg__(self):
        return Vec2D(-self[0], -self[1])

    def __abs__(self):
        return (self[0]**2 + self[1]**2)**0.5

    def rotate(self, angle):
        """rotate self counterclockwise by angle"""
        perp = Vec2D(-self[1], self[0])
        angle = angle * math.pi / 180.0
        c, s = math.cos(angle), math.sin(angle)
        return Vec2D(self[0] * c + perp[0] * s, self[1] * c + perp[1] * s)

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
        x1, y1 = self.pos
        x2, y2 = other.pos
        v1, v2 = self.speed, other.speed

        # s向量是球心连线上的
        s = Vec2D(x2 - x1, y2 - y1)
        s_length = abs(s)
        s = Vec2D(s[0]/s_length, s[1]/s_length)  # 单位化s向量

        # t向量是s的垂直线上的
        t = s.rotate(90)

        # 计算v1（v1x, v1y)在s和t轴的投影值
        v1s = v1 * s  # v1在s轴的分量
        v1t = v1 * t  # v1在t轴的分量
        v2s = v2 * s  # v2在s轴的分量
        v2t = v2 * t  # v2在t轴的分量

        # 交换速度分量
        v1s, v2s = v2s, v1s

        # 将分量转换回向量
        v1s_vector = s * v1s
        v1t_vector = t * v1t
        v2s_vector = s * v2s
        v2t_vector = t * v2t

        # 计算新的速度
        new_v1 = v1s_vector + v1t_vector
        new_v2 = v2s_vector + v2t_vector

        self.speed=new_v1
        other.speed=new_v2

state = {}
def animate(group):
    rect=pygame.rect.Rect((0,0),(width,height))
    screen.fill((255,255,255),rect)
    for i in range(len(group)):
        ball=group[i]
        for j in range(i):
            other=group[j]
            collided = ball.distance(other) < ball.rect.width
            # 避免球下次重复碰撞。碰撞之后，两个球可能暂时仍然是重叠的
            if i!=j:
                if collided and not state.get((i,j),0):
                    ball.collide(other)
                    state[(i,j)] = 1
                elif not collided:
                    state[(i,j)] = 0
    # 更新球位置并绘制球
    for ball in group:
        ball.move()
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
        ball = Ball(image, Vec2D(location), Vec2D(speed))
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
