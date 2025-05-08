import math
import tkinter as tk
import tkinter.ttk as ttk
from time import perf_counter
from turtle import *
from random import randint

G = 50 # 引力常量
d_t = 0.000005 # 一轮计算经过的"时间", 经测试说明越小越精确
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
        # 计算天体自身受到的加速度
        p=earth # 本程序中，假设卫星只受到地球的引力
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
    def calc_orbit(self,parent): # 计算轨道参数
        # 计算相对位置矢量和相对速度矢量
        dx, dy = self.x - parent.x, self.y - parent.y
        vx, vy = self.dx - parent.dx, self.dy - parent.dy
        r = math.hypot(dx, dy)
        v = math.hypot(vx, vy)

        mu = G * (parent.m + self.m)
        ecc_vec = ((v ** 2 - mu / r) * dx - (dx * vx + dy * vy) * vx,
                   (v ** 2 - mu / r) * dy - (dx * vx + dy * vy) * vy)

        ecc = math.hypot(ecc_vec[0], ecc_vec[1]) / mu
        semimajor_axis = 1 / (2 / r - v ** 2 / mu)
        return ecc, semimajor_axis

class Earth(Star): # 地球固定在中心, 继承自Star类
    def gravity(self):
        pass
    def step(self):
        pass

def clear_screen(*_): # 清除行星轨迹,*_ 用于忽略传入的参数
    for p in lst:
        p.clear()
    del lst[2:] # 清除所有备份天体

def get_rand_color(): # 返回随机的颜色
    return (randint(64,192),
            randint(64,192),
            randint(64,192))

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

def acc_satellite():
    backup=Star(sat.m,(sat.x,sat.y),(sat.dx,sat.dy)) # 创建一个备份天体，用于显示卫星变轨前的运动
    backup.color(tuple(int(v) for v in sat.pencolor()))
    backup.hideturtle()

    sat.dx*=1.1
    sat.dy*=1.1
    sat.pencolor(get_rand_color())
def slow_satellite():
    backup=Star(sat.m,(sat.x,sat.y),(sat.dx,sat.dy)) # 创建一个备份天体，用于显示卫星变轨前的运动
    backup.color(tuple(int(v) for v in sat.pencolor()))
    backup.hideturtle()

    sat.dx/=1.1
    sat.dy/=1.1
    sat.pencolor(get_rand_color())
def exit():
    win.destroy();scr.bye() # 关闭窗口
def reset(): # 重置各个天体
    sat.x,sat.y,sat.dx,sat.dy = 100, 0, 0, math.sqrt(2)*500
    sat.color((128,128,128))
    scr.ontimer(clear_screen, 50) # 定时清除旧的轨迹

# 创建tkinter 界面
win=tk.Tk()
win.title("Control")
win.geometry("350x110")
btns=tk.Frame(win)
btns.pack(side=tk.LEFT)

ttk.Button(btns,text="Play",command=play,width=5).grid(row=0,column=1)
ttk.Button(btns,text="Stop",command=stop,width=5).grid(row=0,column=2)
ttk.Button(btns,text="Fast",command=increase_speed,width=5).grid(row=0,column=3)
ttk.Button(btns,text="Slow",command=decrease_speed,width=5).grid(row=0,column=4)
ttk.Button(btns,text="Clear",command=clear_screen,width=5).grid(row=0,column=5)
ttk.Button(btns,text="Reset",command=reset,width=5).grid(row=0,column=6)
ttk.Button(btns,text="Accelerate",command=acc_satellite).grid(row=1,column=1,columnspan=2)
ttk.Button(btns,text="Decelerate",command=slow_satellite).grid(row=1,column=3,columnspan=2)
ttk.Button(btns,text="Exit",command=exit,width=5).grid(row=1,column=5)

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
scr.colormode(255)
scr.onclick(clear_screen) #点击屏幕清屏

w=Turtle() # w 用于输出文字
w.penup();w.hideturtle()
w.color("white") # 设置文字颜色为白色

earth = Earth(1e6, (0,0), (0,0))
earth.penup()
earth.color("blue")
earth.shapesize(2)

sat = Star(1, (100,0), (0,math.sqrt(2)*500))
sat.color((128,128,128))
sat.shapesize(0.7)

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

        ecc, semimajor_axis=sat.calc_orbit(earth)
        # math.hypot(x,y)相当于math.sqrt(x**2+y**2)
        tip="Earth satellite Dist: %.3f\nVelocity: %.3f" % (
                math.hypot(sat.x-earth.x,sat.y-earth.y), math.hypot(sat.dx,sat.dy))
        tip+="\nEccentricity: {:.4g}\tSemimajor Axis: {:.5g}".format(ecc,semimajor_axis)
        w.clear()
        w.goto(scr.window_width()//2-390,
             scr.window_height()//2-60)
        w.write(tip, font=(None,12))
    except (Terminator,tk.TclError):break # 如果窗口已关闭，忽略错误