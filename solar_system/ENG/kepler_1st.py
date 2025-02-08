import math
import tkinter as tk
import tkinter.ttk as ttk
from time import perf_counter
from turtle import *

G = 50 # 引力常量
d_t = 0.000005 # 一轮计算经过的"时间", 经测试说明越小越精确
speed = 600 # 刷新一次屏幕之前执行计算的次数, 越大越快
lst=[]

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

def get_orbit_shape(): # 获取椭圆轨道的长轴两端点坐标, 及焦点F2坐标
    max_x=max(x_lst)
    min_x=min(x_lst)
    middle = (max_x + min_x)/2 # 椭圆中心X坐标, 焦点F1是太阳, X是F1F2的中点
    return min_x,max_x,2 * middle - 0

def clear_screen(*_): # 清除行星轨迹
    for p in lst:
        p.clear()

def play():
    global d_t
    d_t=0.000005
    sp["text"]="Speed: %.2f" % (d_t*10**6)
def stop():
    global d_t
    d_t=0
    sp["text"]="Speed: %.2f" % (d_t*10**6)
def increase_speed():
    global d_t
    d_t*=1.2
    sp["text"]="Speed: %.2f" % (d_t*10**6)
def decrease_speed():
    global d_t
    d_t/=1.2
    sp["text"]="Speed: %.2f" % (d_t*10**6)

def exit():
    win.destroy();scr.bye() # 关闭窗口

# 创建tkinter 界面
win=tk.Tk()
win.title("Control")
win.geometry("260x80")
btns=tk.Frame(win)
btns.pack(side=tk.LEFT)

ttk.Button(btns,text="Play",command=play,width=5).grid(row=0,column=1)
ttk.Button(btns,text="Stop",command=stop,width=5).grid(row=0,column=2)
ttk.Button(btns,text="Fast",command=increase_speed,width=5).grid(row=0,column=3)
ttk.Button(btns,text="Slow",command=decrease_speed,width=5).grid(row=0,column=4)
ttk.Button(btns,text="Clear",command=clear_screen).grid(row=1,column=2,columnspan=2)
ttk.Button(btns,text="Exit",command=exit,width=5).grid(row=1,column=4)

labels=tk.Frame(win)
labels.pack(side=tk.RIGHT,expand=True)

fps=tk.Label(labels,text="FPS: 0")
fps.pack(side=tk.TOP)
sp=tk.Label(labels,text="Speed: %.2f" % (d_t*10**6))
sp.pack(side=tk.TOP)


scr=Screen()
scr.title("Python gravity simulation of Kepler's first law")
scr.bgcolor("black")
scr.tracer(0,0)
scr.onclick(clear_screen) #点击屏幕清屏

w=Turtle() # w 用于输出文字
w.penup();w.hideturtle()
w.color("white") # 设置文字颜色为白色


sun = Sun(1e6, (0,0), (0,0)) # 恒星
sun.penup()
sun.color("yellow")
sun.shapesize(2)

p = Star(1e4, (260,0), (0,300)) # 行星
p.color("blue")
p.shapesize(0.7)

t = 0 # 程序运行的总"时间"
x_lst=[] # 行星与太阳距离的列表
time=perf_counter() # 用于计算FPS
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

    try:
        # 刷新行星
        for p in lst:
            p.update()
        fps["text"]='FPS: %d' % int(1 / (perf_counter()-time))
        update()
    
        time=perf_counter()

        # 验证椭圆轨道
        if t < 1:
            x_lst.append(p.x)
            w.clear()
            w.goto(scr.window_width()//2-310,
                scr.window_height()//2-30)
            w.write("Generating results ...", font=(None,12))
        else:
            x1,x2,x_f2 = get_orbit_shape()
            _2a = x2-x1
            d = math.hypot(p.x,p.y) # 行星到恒星距离
            d2 = math.hypot(x_f2-p.x,p.y) # 行星到焦点F2距离
            # 输出文字
            w.clear()
            w.goto(scr.window_width()//2-310,
                scr.window_height()//2-30)
            w.write("PF1 + PF2= %f 2a= %f"%(d+d2, _2a), font=(None,12)) # 如果PF1+PF2近似等于2a, 则验证通过

            # 画上标签
            w.goto(sun.x, sun.y)
            w.write("   F1", font=(None,12))
            w.pendown()
            w.goto(p.x, p.y)
            w.write(" P", font=(None,12))
            w.goto(x_f2, 0)
            w.dot(5)
            w.write("F2", font=(None,12))
            w.penup()
            # 长轴2a
            w.goto(x1,0)
            w.pendown()
            w.goto(x2,0)
            w.penup()
            w.goto((1.2*x1 + 0.8*x2)/2,0)
            w.write("2a", font=(None,12))
    except (Terminator,tk.TclError):break # 如果窗口已关闭，忽略错误