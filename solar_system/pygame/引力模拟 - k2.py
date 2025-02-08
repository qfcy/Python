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

def distance(p1,p2):
    dx=p1[0]-p2[0];dy=p1[1]-p2[1]
    return math.sqrt(dx**2 + dy**2)
def calc_square(t):
    a=distance(t[0],t[1])
    b=distance(t[1],t[2])
    c=distance(t[0],t[2])
    p = (a+b+c)/2
    return math.sqrt(p*(p-a)*(p-b)*(p-c))
def step(lst):
    global S_total
    surf = pygame.Surface(size)
    surf.fill(color=(200,200,200))
    previous = stars[1].x, stars[1].y # 行星的上一个位置
    for body in lst:
        body.step_once()
    # 开普勒第二定律
    triangle = [center, previous, (stars[1].x, stars[1].y)]
    area.append(triangle)
    S_total += calc_square(triangle)
    for triangle in area:
        pygame.draw.polygon(surf, (0, 100, 255),
                            triangle, width=0)
    previous = stars[1].x, stars[1].y

    for body in lst:
        pygame.draw.circle(surf, body.color, (int(body.x), int(body.y)), body.radius)
    return surf

t = 0.05
size = width,height = 400, 400
center = 100,100

screen = pygame.display.set_mode(size,pygame.RESIZABLE)
screen.fill((255, 255, 255))
stars = [CelestialBody(10000,center,(0,0),10,(255,100,100)),
         CelestialBody(10,(200,100),(0,7),10,(0,50,100))]
area = [] # 行星扫过的区域
S_total = 0 # 行星扫过区域的总面积
time = 0

clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running=False
        elif event.type == pygame.VIDEORESIZE:
            size = width,height = event.size
            screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # 清零
            time = S_total = 0
            area = []

    time += t
    print("时间:%.4f"%time,"行星扫过面积:%.4f"%S_total,
          "行星扫过面积÷时间 = %.4f"%(S_total/time))

    screen.blit(step(stars),(0,0))
    pygame.display.flip()
    clock.tick(120)

pygame.quit()
