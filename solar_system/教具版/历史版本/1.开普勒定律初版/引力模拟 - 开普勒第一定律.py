import math
from turtle import *

G = 50 # 引力常量
d_t = 0.000005 # 一轮计算经过的"时间", 经测试说明越小越精确
speed = 600 # 刷新一次屏幕之前执行计算的次数, 越大越快
lst=[]
x_lst=[] # 行星x坐标的列表

class Star(Turtle):
    def __init__(self, mass, position, velocity):
        super().__init__()
        self.shape("circle")
        self.m=mass # 行星质量
        self.x,self.y=position # 行星初始位置
        self.dx,self.dy=velocity # 行星初始速度
        self.ax=self.ay=0  # 行星加速度
        lst.append(self)
        self.penup()
        self.setpos((self.x,self.y))
        self.pendown()
    def gravity(self):
        # 计算行星自身受到的加速度，以及列表中位于自己之后的行星受到自己引力的加速度
        for i in range(lst.index(self)+1, len(lst)):
            p=lst[i] # 另一个行星
            dx=p.x-self.x
            dy=p.y-self.y

            d = math.hypot(dx,dy) # 相当于 (dx**2 + dy**2)再开根号
            f = G * self.m * p.m / d**2
            # 将力正交分解为水平、竖直方向并计算加速度
            self.ax+=f / self.m * dx / d
            self.ay+=f / self.m * dy / d
            p.ax-=f / p.m * dx / d
            p.ay-=f / p.m * dy / d
    def step(self):
        # 计算行星速度、位移
        self.dx += d_t*self.ax
        self.dy += d_t*self.ay

        self.x+= d_t*self.dx
        self.y+= d_t*self.dy
    def update(self):
        self.setpos((self.x,self.y))

class Sun(Star): # 太阳固定在中心, 继承自Star类
    def gravity(self):
        for i in range(lst.index(self)+1, len(lst)):
            p=lst[i] # 另一个行星
            dx=p.x-self.x
            dy=p.y-self.y

            d = math.hypot(dx,dy)
            f = G * self.m * p.m / d**2
            # 将力正交分解为水平、竖直方向并计算加速度
            p.ax-=f / p.m * dx / d
            p.ay-=f / p.m * dy / d
    def step(self):
        pass

def get_orbit_shape(): # 获取椭圆轨道的长轴长度2a, 及焦点F2坐标
    max_x=max(x_lst)
    min_x=min(x_lst)
    middle = (max_x + min_x)/2 # 椭圆中心X坐标, 焦点F1是太阳(0,0), X是F1F2的中点
    return max_x-min_x,2 * middle - 0

def clear_screen(x,y): # 清除行星轨迹
    for p in lst:
        p.clear()

scr=Screen()
scr.title("Python 天体引力模拟的探索")
scr.bgcolor("black")
scr.tracer(0,0)
scr.onclick(clear_screen) #点击屏幕清屏

sun = Sun(1e6, (0,0), (0,0)) # 恒星
sun.penup()
sun.color("yellow")
sun.shapesize(2)

p = Star(1e4, (260,0), (0,300)) # 行星
p.color("blue")
p.shapesize(0.7)

t = 0 # 程序运行的总"时间"
while True:
    # 计算行星的位置
    for i in range(speed):
        t += d_t
        # 分别计算每个行星受到的加速度
        for p in lst:
            p.gravity()
        # 根据计算的加速度, 求出速度和位移
        for p in lst:
            p.step()
        for p in lst:
            p.ax=p.ay=0 # 重置加速度
    
    # 刷新行星
    for p in lst:
        p.update()
    update()

    # 验证椭圆轨道
    if t < 1:
        x_lst.append(p.x)
    else:
        _2a,x_f2 = get_orbit_shape()
        d = math.hypot(p.x,p.y) # 行星到恒星距离
        d2 = math.hypot(x_f2-p.x,p.y) # 行星到焦点F2距离
        print("PF1 + PF2:",d+d2, "2a:",_2a) # 如果PF1+PF2近似等于2a, 则验证通过
