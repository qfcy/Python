# -*- coding: utf-8 -*-
# 双星系统的模拟
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

class GravSys(solar_system.GravSys):
    # 引力系统
    def __init__(self,scr=None):
        super().__init__(scr)
        self.dt = 0.0004 # 速度
        #speed: 程序在绘制一帧之前执行计算的次数
        self.speed=30
    def increase_speed(self,event=None):
        self.dt+=0.00004
    def decrease_speed(self,event=None):
        self.dt-=0.00004

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
    star1=Star(gs,"恒星1",SUN_MASS/2,(-20,0),(0,223),
               1.2,shape=("yellow",))
    moon1 = Star(gs,"行星",1,(-28,0),(0,900),
               0.5,shape=("gray30",),sun=star1)
    star2=Star(gs,"恒星2",SUN_MASS/2,(20,0),(0,-223),
               1.2,shape=("yellow",))

    # 地球
    earth = Star(gs,"地球1", 1, (260,0), (0,173),
                 0.8,shape=("blue","blue4"),sun=None)
    earth2 = Star(gs,"地球2", 1, (-260,0), (0,-173),
                 0.8,shape=("blue","blue4"),sun=None)
    earth3 = Star(gs,"地球3", 1, (-70,0), (0,-360),
                 0.8,shape=("blue","blue4"),sun=None)

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
    try:gs.start()
    except (Terminator,TclError):pass

if __name__ == '__main__':
    main()
