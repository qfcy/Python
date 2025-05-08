# -*- coding: utf-8 -*-
# 黑洞模拟1。原理：限制行星x轴和y轴方向的速度大小，行星就会往恒星无限下坠。
# 不断减小引力系统的dt, 使行星下坠时不损失模拟精度。
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
    __slots__=solar_system.GravSys.__slots__+["dt_s"]
    def __init__(self,scr=None):
        super().__init__(scr)
        self.dt = 0.001 # 速度
        self.dt_s=1
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
                tip="fps:%d\n日地距离: %s\n放大倍数: %s\n时间速度: %s\n" % (
                    self.fps, str(earth.distance(sun)),
                    str(self.scale),str(self.dt))
                if self.following:
                    tip+="\n正在跟随: %s\n质量: %d" % (
                        self.following.name,self.following.m)
                    if getattr(self.following,'parent',None):
                        tip+="\n到%s距离: %s" % (self.following.parent.name,
                str(self.following.distance(self.following.parent)))

                top_h=26;fontsize=12
                h = (tip.count("\n")+1)*(fontsize*3-4)/2 + top_h # 3和4为调试中推出的数值
                self.writer.clear()
                self.writer.goto(
                    scr.window_width()//2-290,scr.window_height()//2-h
                )
                self.writer.write(
                    tip,
                    font = (None,fontsize)
                )
    def increase_speed(self,event=None):
        self.dt_s*=1.1
    def decrease_speed(self,event=None):
        self.dt_s/=1.1
    def zoom(self,scale): # 缩放
        self.scale *= scale
        #self._update_size()
        self.scr.ontimer(self.clear_scr, max(int(1000/self.fps),17))
    _onrelease=_copy_func(solar_system.GravSys._onrelease,globals()) # 使用本模块中的SpaceCraft类

l=[]
class Star(solar_system.Star):
    def step(self):
        # 计算行星位置
        dt = self.gs.dt
        self.dx += dt*self.ax
        self.dy += dt*self.ay

        d=self.distance(self.sun)
        l.append(d)
        self.gs.dt=0.00002*d*self.gs.dt_s
        # **限制行星的速度**
        MAX=40
        self.dx, self.dy = (max(min(self.dx, MAX),-MAX),
                            max(min(self.dy, MAX),-MAX))
        if d<1e-103:
            print("Dropped",d)

        self.x+= dt*self.dx
        self.y+= dt*self.dy

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
    sun = Sun(gs,"太阳",SUN_MASS, (0,0), (0,0),
              1,has_orbit=False,shape=("circle","yellow"))
    sun.fillcolor("black")

    earth = Star(gs,"地球",EARTH_MASS, (260,0), (0,100),
                 0.8, shape=("blue","#00008b","blue"))

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
    gs.scale=1.5
    gs.init()
    try:gs.start()
    except (Terminator,TclError):pass

if __name__ == '__main__':
    main()
