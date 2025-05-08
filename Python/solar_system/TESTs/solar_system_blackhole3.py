# -*- coding: utf-8 -*-
# 黑洞模拟3。原理：行星绕恒星旋转时，不断减速，行星将会往恒星无限下坠。
# 不断减小引力系统的dt, 使行星下坠时不损失模拟精度。
# 另外，行星下坠到一定程度时程序会溢出
import sys,os
try:
    import solar_system # 导入主模块
    from solar_system import *
    from solar_system import _copy_func
except ImportError:
    sys.path.append(os.path.join(os.path.split(__file__)[0],"..")) # 避免导入失败
    import __init__ as solar_system;from __init__ import *
    from __init__ import _copy_func

from time import perf_counter
from random import randrange
import math,turtle,pickle
from turtle import *
from tkinter import TclError

__version__="1.3.3"

SUN_MASS=1000000
EARTH_MASS=9000

class GravSys(solar_system.GravSys):
    # 引力系统
    __slots__=solar_system.GravSys.__slots__+["dt_k","scale_k"]
    def __init__(self,scr=None):
        super().__init__(scr)
        self.dt = 0.0005 # 实际速度
        self.dt_k=0.000005 # 速度
        #speed: 程序在绘制一帧之前跳过的帧数
        self.speed=100
        self.scale=1 # 实际放大倍数
        self.scale_k=200 # 用户调节的放大倍数
    def start(self): # 主循环, 最关键的函数
        scr = self.scr
        while True:
            # 计算行星的位置
            for _ in range(self.speed):
                self.t += self.dt
                for p in self.planets: # 计算各行星加速度
                    p.acc()
                for p in self.planets: # 计算速度、位移
                    p.step()
                for p in self.planets:
                    p.ax=p.ay=0
            if self.following!=None:
                self.scr_x=-self.following.x+self.key_x
                self.scr_y=-self.following.y+self.key_y
            else:
                self.scr_x=self.key_x
                self.scr_y=self.key_y
            # 刷新行星
            for p in self.planets:
                p.update()
            update()
            self.fps=1/(perf_counter()-self.__last_time) # 计算帧率
            self.__last_time=perf_counter()

            # 显示文字
            if self.show_tip:
                self.writer.clear()
                self.writer.goto(
                    scr.window_width()//2-280,scr.window_height()//2-80
                )
                sun,earth = self.planets[0],self.planets[1]
                self.writer.write("fps:%d\n日地距离：%s\n放大倍数：%s" % (
                    self.fps,
                    str(earth.distance(sun)),
                    str(self.scale)),
                font = (None,12)
                )
    def increase_speed(self,event=None):
        self.dt_k*=1.1
    def decrease_speed(self,event=None):
        self.dt_k/=1.1
    def zoom(self,event):
        if event.keysym=="equal":
            # 放大
            self.scale_k*=1.8
        else:
            # 缩小
            self.scale_k/=1.8
        #self._update_size()
        self.scr.ontimer(self.clear_scr, max(int(1000/self.fps),17))
    _onrelease=_copy_func(solar_system.GravSys._onrelease,globals()) # 使用本模块中的SpaceCraft类

l=[]
class Star(solar_system.Star):
    def __init__(self, *args, **kw):
        super().__init__(*args,**kw)
        self.dropped = False # 是否已坠入
    def acc(self):
        # ** 计算行星的引力、加速度 **
        G = self.gs.G
        for i in range(self._index+1,len(self.gs.planets)):
            planet=self.gs.planets[i]
            dx=planet.x-self.x
            dy=planet.y-self.y
            try:
                # 简化前的代码
                #r = math.hypot(dx,dy)
                #f = G * self.m * planet.m / r**2
                # 将力分解为水平、竖直方向的力
                #ax+=f / self.m * dx / r
                #ay+=f / self.m * dy / r
                r = math.hypot(dx,dy)
                b = G / r ** 2
                self.ax+=b * dx * planet.m / r
                self.ay+=b * dy * planet.m / r
                planet.ax-=b * dx * self.m / r
                planet.ay-=b * dy * self.m / r
            except ZeroDivisionError:pass
    def step(self):
        # 计算行星位置
        dt = self.gs.dt
        self.dx += dt*self.ax
        self.dy += dt*self.ay

        self.x+= dt*self.dx
        self.y+= dt*self.dy

        self.d=self.distance(self.sun)
        self.gs.scale = self.gs.scale_k / self.d ** 0.98 # 0.98：行星落入“黑洞”动画的速度
        l.append(self.d)
        self.gs.dt=self.d**(3/2)*self.gs.dt_k
        if self.d > 1e-150 and not self.dropped:
            #speed=100/math.hypot(*self.v) # 另一种
            #self.v*=pow(speed,max(dt,0.00004)
            self.dx *= 0.999;self.dy *=0.999 # 使行星不断减速
        else: # 如果self.d极小，已经接近溢出(约2.1e-151时)
            self.dropped=True
            self.gs.dt_k = 2e-7

class RoundStar(solar_system.RoundStar,Star):
    def __init__(self, *args, **kw):
        super().__init__(*args,**kw)
        self.dropped = False

class Sun(solar_system.Sun,Star):
    def __init__(self, *args, **kw):
        super().__init__(*args,**kw)
        self.dropped = False

class SpaceCraft(solar_system.SpaceCraft,Star):
    def __init__(self, *args, **kw):
        super().__init__(*args,**kw)
        self.dropped = False

FLAG_SAVEFILE = False # 退出时是否自动保存数据到game.pkl
def main():
    scr=Screen()
    scr.screensize(6000,6000)
    try:
        scr._canvas.master.state("zoomed")
    except TclError:pass
    scr.bgcolor("black")
    scr.tracer(0,0)

    gs = GravSys(scr)
    sun = Sun(gs,"太阳",SUN_MASS, (0,0), (0,0),
              3,has_orbit=False,shape=("circle","yellow"))
    sun.fillcolor("black")

    # 地球
    earth = Star(gs,"地球",EARTH_MASS, (260,0), (0,173),
                 2.1, shape=("blue","blue4"))

    # 绑定键盘事件
    cv=scr.getcanvas()
    cv.bind_all("<Key-Up>",gs.up)
    cv.bind_all("<Key-Down>",gs.down)
    cv.bind_all("<Key-Left>",gs.left)
    cv.bind_all("<Key-Right>",gs.right)
    cv.bind_all("<Key-equal>",gs.increase_speed)
    cv.bind_all("<Key-minus>",gs.decrease_speed)
    cv.master.bind("<Key-Tab>",gs.switch) # 修复python 3.10+下无法绑定的bug
    cv.bind_all("<Key-Delete>",gs.del_planet)
    cv.master.bind("<Shift-Key-Tab>",gs.reverse_switch)
    cv.bind_all("<Control-Key-equal>",gs.zoom) #Ctrl+"+"
    cv.bind_all("<Control-Key-minus>",gs.zoom) #Ctrl+"-"
    cv.bind_all("<Control-Key-d>",gs.clear_spacecrafts)
    cv.bind("<Button-1>",gs._onclick)
    cv.bind("<B1-Motion>",gs._ondrag)
    cv.bind("<B1-ButtonRelease>",gs._onrelease)

    globals().update(locals()) # 便于程序退出后, 在交互模式(>>> )中调试程序
    gs.init()
    try:gs.start()
    except (Terminator,TclError):pass
    #print(l[-100:])

if __name__ == '__main__':
    main()
