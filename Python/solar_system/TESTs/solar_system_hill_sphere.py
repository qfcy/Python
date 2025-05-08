# -*- coding: utf-8 -*-
# 程序为希尔球，及拉格朗日点的模拟。
# 希尔球指行星的卫星可能分布的区域，
# 卫星到行星的距离不能超过希尔球半径，否则，卫星将被恒星的潮汐力扯离行星。
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

class GravSys(solar_system.GravSys):
    # 引力系统
    def __init__(self,scr=None):
        super().__init__(scr)
        self.speed=20
    _onrelease=_copy_func(solar_system.GravSys._onrelease,globals()) # 使用本模块中的SpaceCraft类

class Star(solar_system.Star):
    def getOrbitSpeed(self,r=None,other=None):
        # 获取某一半径的圆轨道上天体的速率
        # 引力=向心力=m * v**2 / r
        other=other or self.sun
        r=r or self.distance(other)
        return math.sqrt(self.grav(other,r) * r / self.m)
    def getHillSphere(self,other=None):
        # 获取行星希尔球半径
        # 希尔球是环绕在天体（像是行星）周围的空间区域，其中被它吸引的天体受到它的控制，而不是被它绕行的较大天体（像是恒星）所控制。
        other=other or self.parent
        return self.distance(other) * (self.m/(other.m*3)) ** (1/3)

class RoundStar(solar_system.RoundStar,Star):
    pass

class Sun(solar_system.Sun,Star):
    pass

class SpaceCraft(solar_system.SpaceCraft,Star):
    pass

FLAG_SAVEFILE = False # 退出时是否自动保存数据到game.pkl
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
              2.3,has_orbit=False,shape=('yellow',))
    # 地球
    r_earth = 2000
    earth = Star(gs,"地球",100, (r_earth,0), (0,173),
                 0.6, shape=("blue","#00008b","blue"))
    earth.dy=earth.getOrbitSpeed()
    # 卫星
    r_hill=earth.getHillSphere()
    print("地球希尔球大小:",r_hill)
    moons=[]
    for i in range(10):
        moon=Star(gs,"卫星%d"%(i+1),1e-50, (r_earth+r_hill*(0.1*i+0.1),0), (0,0),
                 0.1,shape=("gray",),parent=earth)
        moon.dy=earth.dy+moon.getOrbitSpeed(other=earth)
        moons.append(moon)

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
    gs.follow(earth)
    try:gs.start()
    except (Terminator,TclError):pass
    if FLAG_SAVEFILE or len(sys.argv)==2:
        with open(file,'wb') as f: # 保存数据
            pickle.dump(gs,f)

if __name__ == '__main__':
    main()
