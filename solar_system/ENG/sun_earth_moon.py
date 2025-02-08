import math
import tkinter as tk
import tkinter.ttk as ttk
from time import perf_counter
from turtle import *

G = 50 # 引力常量
d_t = 0.000008 # 一轮计算经过的"时间", 经测试说明越小越精确
speed = 200 # 刷新一次屏幕之前执行计算的次数, 越大越快
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

def clear_screen(*_): # 清除行星轨迹
    for p in lst:
        p.clear()

def play():
    global d_t
    d_t=0.000008
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

def acc_planet():
    global t,S
    t=1e-10; S=0 # 重置时间和扫过面积
    earth.dx*=1.1
    earth.dy*=1.1
    moon.dx += earth.dx*0.1
    moon.dy += earth.dy*0.1
def slow_planet():
    global t,S
    t=1e-10; S=0 # 重置时间和扫过面积
    earth.dx/=1.1
    earth.dy/=1.1
    moon.dx -= earth.dx* 1/9
    moon.dy -= earth.dy* 1/9
def zoom_earth_orbit(scale): # 扩大/缩小地球轨道,scale为比例
    x,y,dx,dy=earth.x,earth.y,earth.dx,earth.dy # 存储地球旧的位置、速度
    earth.x*=scale # 改变地球位置
    earth.y*=scale
    # 改变地球速度
    earth.dx/=math.sqrt(scale) # 根据GM/R² = mv²/R, 得速度v与√R成反比
    earth.dy/=math.sqrt(scale)
    moon.x += earth.x-x # 使月球和地球改变相同的位置、速度
    moon.y += earth.y-y
    moon.dx += earth.dx-dx
    moon.dy += earth.dy-dy
def inc_rd(): # 日地距离+
    zoom_earth_orbit(1.1)
def dec_rd(): # 日地距离-
    zoom_earth_orbit(1/1.1)
def zoom_moon_orbit(scale): # 等比例改变月轨道
    x,y,dx,dy=moon.x-earth.x,moon.y-earth.y,\
               moon.dx-earth.dx,moon.dy-earth.dy # 存储月球相对地球位置、速度
    moon.x = earth.x + x * scale # 改变月球位置
    moon.y = earth.y + y * scale
    moon.dx = earth.dx + dx/math.sqrt(scale) # 改变月球速度
    moon.dy = earth.dy + dy/math.sqrt(scale)
def inc_yd(): # 月地距离+
    zoom_moon_orbit(1.1)
def dec_yd(): # 月地距离-
    zoom_moon_orbit(1/1.1)

def exit():
    win.destroy();scr.bye() # 关闭窗口

# 创建tkinter 界面
win=tk.Tk()
win.title("Control")
win.geometry("320x150")
btns=tk.Frame(win)
btns.pack(side=tk.LEFT)

ttk.Button(btns,text="Play",command=play,width=5).grid(row=0,column=1)
ttk.Button(btns,text="Stop",command=stop,width=5).grid(row=0,column=2)
ttk.Button(btns,text="Fast",command=increase_speed,width=5).grid(row=0,column=3)
ttk.Button(btns,text="Slow",command=decrease_speed,width=5).grid(row=0,column=4)
ttk.Button(btns,text="Clear",command=clear_screen,width=5).grid(row=0,column=5)
ttk.Button(btns,text="Accelerate",command=acc_planet).grid(row=1,column=1,columnspan=2)
ttk.Button(btns,text="Decelerate",command=slow_planet).grid(row=1,column=3,columnspan=2)
ttk.Button(btns,text="Sun Earth +",command=inc_rd).grid(row=2,column=1,columnspan=2)
ttk.Button(btns,text="Sun Earth -",command=dec_rd).grid(row=2,column=3,columnspan=2)
ttk.Button(btns,text="Moon Earth +",command=inc_yd).grid(row=3,column=1,columnspan=2)
ttk.Button(btns,text="Moon Earth -",command=dec_yd).grid(row=3,column=3,columnspan=2)
ttk.Button(btns,text="Exit",command=exit,width=5).grid(row=1,column=5)
tk.Label(btns,text="Tips:Improper orbit radius can cause\ninstability in the moon orbit.",
         font=("Microsoft Yahei",8)).grid(row=4,column=1,columnspan=4)

labels=tk.Frame(win)
labels.pack(side=tk.RIGHT,expand=True)

fps=tk.Label(labels,text="FPS: 0")
fps.pack(side=tk.TOP)
sp=tk.Label(labels,text="Speed: %.2f" % (d_t*10**6))
sp.pack(side=tk.TOP)


scr=Screen()
scr.title("Python gravity simulation")
scr.bgcolor("black")
scr.tracer(0,0)
scr.onclick(clear_screen) #点击屏幕清屏

w=Turtle() # w 用于输出文字
w.penup();w.hideturtle()
w.color("white") # 设置文字颜色为白色

sun = Sun(1e6, (0,0), (0,0))
sun.penup()
sun.color("yellow")
sun.shapesize(2)

earth = Star(1e4, (260,0), (0,400))
earth.color("blue")
earth.shapesize(0.7)

moon = Star(1,(269,0), (0,600))
moon.color("gray")
moon.shapesize(0.5)

t = 0 # 程序运行的总"时间"
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
        update()
    
        fps["text"]='FPS: %d' % int(1 / (perf_counter()-time))
        time=perf_counter()

        w.clear()
        w.goto(scr.window_width()//2-260,
             scr.window_height()//2-60)
        w.write("Sun Earth Distance: %.3f " % math.hypot(sun.x-earth.x,sun.y-earth.y) + "\n" + \
                "Moon Earth Distance: %.3f" % math.hypot(moon.x-earth.x,moon.y-earth.y)
                , font=(None,12))
    except (Terminator,tk.TclError):break # 如果窗口已关闭，忽略错误