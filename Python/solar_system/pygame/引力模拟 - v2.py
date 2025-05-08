import pygame
import math

G = 1 # 引力常量
class CelestialBody: # 天体类
    def __init__(self, mass, position, velocity,radius,color):
        self.m=mass
        self.x,self.y=position
        self.v_x, self.v_y=velocity
        self.radius=radius # 在屏幕上的显示大小
        self.color=color
    def acceleration(self):
        # 计算行星的引力及加速度
        a_x=0; a_y=0
        for other in stars:
            if other == self:continue
            diff_x=other.x-self.x # 另一个天体与自身的距离差
            diff_y=other.y-self.y
            r = math.sqrt(diff_x**2 + diff_y**2) # 距离
            g = G * other.m / r**2
            # 正交分解为水平、竖直方向
            a_x += g / r * diff_x # 将各天体引力产生的加速度进行累加
            a_y += g / r * diff_y
        return a_x, a_y
    def step_once(self): # 单次计算
        # 计算行星位置
        a_x, a_y = self.acceleration()
        self.v_x += a_x * t # t为单次计算经过的时间
        self.v_y += a_y * t

        self.x+= self.v_x * t
        self.y+= self.v_y * t

    def get_v1(self, r):
        # 获取半径为r的轨道的环绕速度(第一宇宙速度)
        # 引力=向心力=m * v**2 / r
        g = G * self.m / r**2
        return math.sqrt(g * r)
    def get_distance(self,other):
        diff_x = other.x - self.x  # 另一个天体与自身的距离差
        diff_y = other.y - self.y
        return math.sqrt(diff_x**2 + diff_y**2)

def step(lst):
    surf = pygame.Surface(size)
    surf.fill(color=(200,200,200))
    for body in lst:
        body.step_once()
        pygame.draw.circle(surf,body.color,(int(body.x),int(body.y)),body.radius) # 画出各个天体
    for i in range(len(path)-1): # 画出轨迹
        pygame.draw.line(surf,(0,50,100),path[i],path[i+1],1)
    path.append((stars[1].x,stars[1].y))
    return surf

t = 0.04
size = width,height = 400, 400
screen = pygame.display.set_mode(size,pygame.RESIZABLE)
screen.fill((255, 255, 255))

center=CelestialBody(10000,(100,100),(0,0),10,(255,100,100))
v1 = center.get_v1(100)
planet=CelestialBody(10,(200,100),(0,v1*math.sqrt(2)),
                     10,(0,50,100))
stars = [center,planet]
path = [] # 行星经过的路径(轨迹)

clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running=False
        elif event.type == pygame.VIDEORESIZE:
            size = width,height = event.size
            screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
    screen.blit(step(stars),(0,0))
    pygame.display.flip()
    print(center.get_distance(planet))
    #clock.tick(120)

pygame.quit()
