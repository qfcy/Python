# -*- coding: utf-8 -*-
# 使用C语言编写Python扩展，提高程序性能的测试
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
import math,turtle,pickle,warnings
from turtle import *
from tkinter import TclError
from solar_system_accelerate_util import accelerate

__version__="1.3.3"

class GravSys(solar_system.GravSys):
    # 引力系统
    def __init__(self,scr=None):
        super().__init__(scr)
        self.dt = 0.00006 # 速度
        #speed: 程序在绘制一帧之前执行计算的次数
        self.speed=340
    def start(self): # 主循环, 最关键的函数
        scr = self.scr
        for i in range(len(self.planets)):
            p=self.planets[i]
            if isinstance(p,Sun):
                sun_index=i;break
        else:sun_index=-1
        while True:
            self.t += self.dt * self.speed
            # 计算行星的位置,使用Python扩展加速
            accelerate(self.planets,self.G,self.dt,self.speed,Sun)

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
                tip = "fps:%d\n放大倍数: %.4f\n时间速度: %.6f\n" % (
                        self.fps, self.scale, self.dt)
                if self.following:
                    follow = self.following
                    tip += "\n正在跟随: %s\n质量: %d" % (follow.name,follow.m)
                    if getattr(follow,'parent',None):
                        tip+="\n到%s距离: %d" % (follow.parent.name,
                                follow.distance(follow.parent))
                    if isinstance(follow,SpaceCraft):
                        if getattr(follow,'parent',None):
                            # 计算飞船相对父天体速度
                            dx,dy = follow.dx-follow.parent.dx, \
                                    follow.dy-follow.parent.dy
                        else:dx,dy = follow.dx, follow.dy
                        tip+="\n飞船速度: %.6f" % math.hypot(dx,dy) # hypot相当于math.sqrt(dx**2+dy**2)
                        tip+="\n按↑,↓,←,→键控制飞船"

                top_h=26;fontsize=12
                h = (tip.count("\n")+1)*(fontsize*3-4)/2 + top_h # 3和4为调试中推出的数值
                self.writer.clear()
                self.writer.goto(
                    scr.window_width()//2-205,scr.window_height()//2-h
                )
                self.writer.write(
                    tip,
                    font = (None,fontsize)
                )
    def increase_speed(self,event=None):
        self.dt+=0.000006
    def decrease_speed(self,event=None):
        self.dt-=0.000006
    _onrelease=_copy_func(solar_system.GravSys._onrelease,globals()) # 使用本模块中的SpaceCraft类

class Star(solar_system.Star):
    def init(self):
        self.update() # 使行星的turtle移动到初始位置
        self.clear() # 清除轨迹
        self.m=float(self.m);self.x=float(self.x);self.y=float(self.y)
        self.dx=float(self.dx);self.dy=float(self.dy)
        if self.has_orbit:
            self.pendown()
    def acc(self):
        # ** 计算行星的引力、加速度 **
        pass
    def step(self):
        # 计算行星位置
        pass

class RoundStar(solar_system.RoundStar,Star):
    pass

class Sun(solar_system.Sun,Star):
    # 太阳不移动, 固定在引力系统的中心
    def acc(self):
        pass

class SpaceCraft(solar_system.SpaceCraft,Star):
    pass

FLAG_SAVEFILE = False # 退出时是否自动保存数据到game.pkl
main=_copy_func(solar_system.main,globals())

if __name__ == '__main__':
    main()
