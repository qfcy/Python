# -*- coding: utf-8 -*-
# 本程序中的小行星使用计算更快的粒子，用于加快计算速度
# 粒子不影响其他天体运动，粒子的运动仅受部分天体影响
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

PLANET_SIZE=8 # 像素

# 各个行星的质量
SUN_MASS=1000000

MERCURY_MASS=125
VENUS_MASS=8000
EARTH_MASS=9000
MOON_MASS=30
MARS_MASS=700
PHOBOS_MASS=2
AST_MASS=2

JUPITER_MASS=12000
SATURN_MASS=6000
URANUS_MASS=9000
NEPTUNE_MASS=8000
SPACECRAFT_MASS = 1

scr=None

class GravSys(solar_system.GravSys):
    # 引力系统
    _onrelease=_copy_func(solar_system.GravSys._onrelease,globals()) # 使用本模块中的SpaceCraft类

class Star(solar_system.Star):
    def acc(self):
        # ** 计算行星的引力、加速度 **
        G = self.gs.G
        for i in range(self._index+1,len(self.gs.planets)):
            planet=self.gs.planets[i]
            if not isinstance(planet,Particle): # 若不是粒子
                dx=planet.x-self.x
                dy=planet.y-self.y
                try:
                    # 简化前的代码
                    #r = math.hypot(dx,dy)
                    #f = G * self.m * planet.m / r**2
                    # 将力分解为水平、竖直方向的力
                    #ax+=f / self.m * dx / r
                    #ay+=f / self.m * dy / r
                    b = G / math.hypot(dx,dy)**3
                    self.ax+=b * dx * planet.m
                    self.ay+=b * dy * planet.m
                    planet.ax-=b * dx * self.m
                    planet.ay-=b * dy * self.m
                except ZeroDivisionError:pass

class RoundStar(solar_system.RoundStar,Star):
    pass

class Particle(Star): # 使用方法与Star相同，但为粒子形式
    def __init__(self,*args,affect_bodies=None,**kw):
        super().__init__(*args,**kw)
        self.affect_bodies=affect_bodies or [self.sun]
    def acc(self):
        G = self.gs.G
        for planet in self.affect_bodies:
            dx=planet.x-self.x
            dy=planet.y-self.y
            try:
                b = G / math.hypot(dx,dy)**3
                self.ax+=b * dx * planet.m
                self.ay+=b * dy * planet.m
                # 不计算自身对其他天体的影响
            except ZeroDivisionError:pass

class RoundParticle(RoundStar,Particle): # 使用与RoundStar相同，但为粒子
    def __init__(self,*args,affect_bodies=None,**kw):
        super().__init__(*args,**kw)
        self.affect_bodies=affect_bodies or [self.sun]

class Sun(solar_system.Sun,Star):
    # 太阳不移动, 固定在引力系统的中心
    def acc(self):
        G = self.gs.G
        for i in range(self._index+1,len(self.gs.planets)):
            planet=self.gs.planets[i]
            if not isinstance(planet,Particle): # 若不是粒子
                dx=planet.x-self.x
                dy=planet.y-self.y
                try:
                    b = G * self.m / math.hypot(dx,dy)**3
                    planet.ax-=b * dx
                    planet.ay-=b * dy
                except ZeroDivisionError:pass


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

    # 保存数据功能，类似沙盒。不支持python 2
    if len(sys.argv)==2: # 如果有打开文件
        file = sys.argv[1]
    elif FLAG_SAVEFILE: # 如果是退出时保存数据
        file = "game.pkl"
    else:
        file = ""
    if os.path.isfile(file):
        with open(file,'rb') as f:
            gs=pickle.load(f)
    else:
        # 创建天体
        gs = GravSys(scr)
        sun = Sun(gs,"太阳",SUN_MASS, (0,0), (0,0),
                  2.3,has_orbit=False,shape=('yellow',))

        mercury = Star(gs,"水星",MERCURY_MASS, (60,0), (0,330),
                       0.5, shape=("#b3b3b3","#7f7f7f","#4d4d4d"))

        venus = Star(gs,"金星",VENUS_MASS, (-130,0), (0,-250),
                     0.7, shape=("gold","brown","gold4"))

        earth = Star(gs,"地球",EARTH_MASS, (260,0), (0,173),
                     0.8, shape=("blue","#00008b","blue"))

        moon = Star(gs,"月球",MOON_MASS, (269,0), (0,262),
                    0.5,shape=("#b3b3b3","#4d4d4d","gray30"),
                    has_orbit=False, parent=earth)

        mars = Star(gs,"火星",MARS_MASS, (0,430), (-140, 0),
                    0.6, shape=("red","#8b0000"))
        phobos = Star(gs,"火卫一",PHOBOS_MASS, (0,438), (-167, 0),
                      0.1,shape=("orange",),
                      has_orbit=False,parent=mars)
        phobos.fillcolor("orange")

        # 木星及卫星
        jupiter = Star(gs, "木星", JUPITER_MASS, (1100,0), (0, 86),
                       1.2,shape=("#ffd39b","#8b7355","#8b6508"))
        mw1 = Star(gs,"木卫一", MOON_MASS, (1125,0), (0,145),
                   0.05, shape=("yellow",),
                   has_orbit=False,parent=jupiter)
        mw2 = Star(gs,"木卫二", MOON_MASS, (1142,0), (0,134),
                   0.07,shape=("#cd950c",),
                   has_orbit=False,parent=jupiter)
        # 土星
        saturn = Star(gs,"土星",SATURN_MASS, (2200,0), (0, 60),
                      1.0, shape=("#fff68f","#8b864e","#8b864e"))
        # 天王星
        uranus = Star(gs, "天王星", URANUS_MASS, (0, 4300), (-43, 0),
                      0.8, shape=("#add8e6","blue","blue"))
        # 海王星
        neptune = Star(gs, "海王星", NEPTUNE_MASS, (7500,0), (0, 34),
                       0.8, shape=("blue","#483d8b","#191970"))
        hw2 = Star(gs, "海卫二", MOON_MASS, (7600,0), (0, 48),
                   0.16, shape=("square","gray30"),
                   has_orbit=False,parent=neptune)

        # 创建小行星
        # affect_bodies为能影响粒子运动的天体
        affect = [sun,mercury,venus,earth,mars,jupiter,saturn,uranus,neptune]
        for i in range(10):
            ast=RoundParticle(gs,"小行星%d"%i, AST_MASS,(0,0),(0,0),
                          0.05, affect_bodies=affect,has_orbit=False)
            ast.setheading(randrange(360))
            ast.forward(randrange(700,800))
            ast.x,ast.y=ast.pos()
            v = ast.pos().rotate(90)
            ast.dx,ast.dy=v[0]/7,v[1]/7
            ast.pu()
            ast.color("gray")

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
    if FLAG_SAVEFILE or len(sys.argv)==2:
        with open(file,'wb') as f: # 保存数据
            pickle.dump(gs,f)

if __name__ == '__main__':
    main()
