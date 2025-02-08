# -*- coding: utf-8 -*-
# 分子间作用力的简单模拟。原理：两分子在距离较大时受到引力，较小时则受到斥力
# 技巧：拖动鼠标发射飞船，撞击“分子”，即可增加分子的“内能”。
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

AST_MASS=5

class GravSys(solar_system.GravSys):
    # 引力系统
    def __init__(self,scr=None):
        self.scr = scr or Screen()
        self.planets = []
        self.removed_planets=[]
        self.G = 8
        self.t = 0
        self.dt = 0.01 # 速度
        #speed: 程序在绘制一帧之前执行计算的次数
        self.speed=50
        self.scale=1 # 缩放比例
        self.scr_x=self.key_x=0 # scr_x,scr_y:视野的偏移距离
        self.scr_y=self.key_y=0
        self.show_tip=True;self.fps=20
        self.show_orbit=True
        self.startx=self.starty=None
        w=self.writer=Turtle()
        w.ht();w.pu();w.color("white")
        p=self.pen=Turtle()
        p.ht();p.pu();p.color("green")

        #following: 跟随某个行星
        self.following=None
    def increase_speed(self,event=None): # 修改
        self.dt*=1.1
    def decrease_speed(self,event=None):
        self.dt/=1.1
    _onrelease=_copy_func(solar_system.GravSys._onrelease,globals()) # 使用本模块中的SpaceCraft类

class Star(solar_system.Star):
    def acc(self):
        # ** 计算行星的引力、加速度 **
                                                 
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
                F = self.grav(planet)
                b = F / math.hypot(dx,dy)
                self.ax+=b * dx * planet.m
                self.ay+=b * dy * planet.m
                planet.ax-=b * dx * self.m
                planet.ay-=b * dy * self.m
            except ZeroDivisionError:pass
    def grav(self,other,r=None):
        # 计算两行星间的"分子间作用力"
        if r is None:
            dx=other.x-self.x; dy=other.y-self.y
            r = math.hypot(dx,dy)
        k=1000
        # 分子间作用力在距离大于r0时表现为引力，小于r0时表现为斥力(非真实公式)
        return self.gs.G * self.m * other.m / r**2 - k * self.m * other.m / r**3

class RoundStar(solar_system.RoundStar,Star):
    pass

class Sun(solar_system.Sun,Star):
    pass

class SpaceCraft(solar_system.SpaceCraft,Star):
    pass

def main():
    scr=Screen()
    scr.screensize(6000,6000)
    try:
        scr._canvas.master.state("zoomed")
    except TclError:pass
    scr.bgcolor("black")
    scr.tracer(0,0)

    # 创建天体
    gs = GravSys(scr)
    # 多种不同的"分子"模拟，备用
    #p1=RoundStar(gs,"小行星1", AST_MASS,(63,0),(0,0),1) # 简单的两个分子
    #p3=RoundStar(gs,"小行星2", AST_MASS,(-63,0),(0,0),1)
#     # 六边形
#     d=109
#     ast0=RoundStar(gs,"小行星", AST_MASS,(0,0),(0,0),1)
#     for i in range(6):
#         ast=RoundStar(gs,"小行星%d"%i, AST_MASS,(0,0),(0,0),1)
#         ast.setheading(i*60)
#         ast.forward(d)#randrange(700,800))
#         ast.x,ast.y=ast.pos()
#         ast.color("green")
#     # 正方形
#     d=70 
#     for i in range(0,d*6,d):
#         for j in range(0,d*6,d):
#             ast=RoundStar(gs,"小行星%d"%i, AST_MASS,(i,j),(0,0),1)
#             ast.color("green")
    # 较大的六边形
    d=85
    ast0=RoundStar(gs,"小行星", AST_MASS,(0,0),(0,0),1)
    for i in range(6):
        ast=RoundStar(gs,"小行星%d"%i, AST_MASS,(0,0),(0,0),1)
        ast.setheading(i*60)
        ast.forward(d)
        ast.x,ast.y=ast.pos()
        ast.color("green")
    for i in range(6):
        ast=RoundStar(gs,"小行星%d"%i, AST_MASS,(0,0),(0,0),1)
        ast.setheading(i*60)
        ast.forward(2*d)
        ast.x,ast.y=ast.pos()
        ast.color("green")
    for i in range(6):
        ast=RoundStar(gs,"小行星%d"%i, AST_MASS,(0,0),(0,0),1)
        ast.setheading(i*60+30)
        ast.forward(math.sqrt(3)*d)
        ast.x,ast.y=ast.pos()
        ast.color("green")


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
    cv.bind_all("<Control-Key-equal>",lambda event:gs.zoom(4/3.0)) #Ctrl+"+"
    cv.bind_all("<Control-Key-minus>",lambda event:gs.zoom(3/4.0)) #Ctrl+"-"
    cv.bind_all("<Control-Key-d>",gs.clear_spacecrafts)
    cv.bind("<Button-1>",gs._onclick)
    cv.bind("<B1-Motion>",gs._ondrag)
    cv.bind("<B1-ButtonRelease>",gs._onrelease)

    globals().update(locals()) # 便于程序退出后, 在交互模式(>>> )中调试程序
    gs.init()
    gs.switchpen() # 隐藏轨道
    try:gs.start()
    except (Terminator,TclError):pass

if __name__ == '__main__':
    main()
