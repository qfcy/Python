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

def get_orbit_shape(): # 获取椭圆轨道的长、短轴长度, 及中点x坐标
    max_x=max(x_lst)
    min_x=min(x_lst)
    return max_x-min_x,max(y_lst)-min(y_lst),(max_x + min_x)/2
def step(lst):
    global x_max,y_max
    surf = pygame.Surface(size)
    surf.fill(color=(200,200,200))
    for body in lst:
        body.step_once()
        pygame.draw.circle(surf,body.color,(int(body.x),int(body.y)),body.radius) # 画出各个天体
    for i in range(len(path)-1): # 画出轨迹
        pygame.draw.line(surf,(0,50,100),path[i],path[i+1],1)
    path.append((stars[1].x,stars[1].y))
    return surf

t = 0.08
size = width,height = 400, 400
screen = pygame.display.set_mode(size,pygame.RESIZABLE)
screen.fill((255, 255, 255))
stars = [CelestialBody(10000,(100,100),(0,0),10,(255,100,100)),
         CelestialBody(10,(200,100),(0,7),10,(0,50,100))]
x_lst=[];y_lst=[]
time = 0
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
    clock.tick(120)

    time += t
    if time>30:
        w,h,centerx = get_orbit_shape()
        print((stars[1].x-centerx)**2 + \
              (w/h * (stars[1].y-stars[0].y))**2) # 椭圆的方程, 输出结果为一个定值

    x_lst.append(stars[1].x)
    y_lst.append(stars[1].y)

pygame.quit()
