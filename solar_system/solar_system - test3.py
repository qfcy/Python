# -*- coding: utf-8 -*-
"""
使用turtle模块的太阳系模拟程序

快捷键:
按Ctrl+“+”或Ctrl+“-”进行缩放。
按↑，↓，←，→键移动。
按“+”或“-”键增加或者降低速度。
单击屏幕开启或关闭轨道显示。
单击行星即可跟随该行星。
"""
try:
    from time import perf_counter
# 兼容 Python 2 与 Python 3
except ImportError:from time import clock as perf_counter
from random import randrange
import math,turtle
from turtle import *

Vec=Vec2D
try:
    from tkinter import TclError
except ImportError:
    from Tkinter import TclError

__author__="七分诚意 qq:3076711200"
__email__="3416445406@qq.com"
__version__="1.1.1"

G = 8
PLANET_SIZE=8 # 像素

# 各个行星的质量
SUN_MASS=1000000

MERCURY_MASS=125
VENUS_MASS=3000
EARTH_MASS=4000
MOON_MASS=1
MARS_MASS=600
PHOBOS_MASS=2
AST_MASS=2

JUPITER_MASS=7000
SATURN_MASS=6000
URANUS_MASS=9000
NEPTUNE_MASS=8000

scr=None

class GravSys:
    # 引力系统
    __slots__=['planets', 'removed_planets', 't', 'dt', 'speed',
               'scale', 'scr_x', 'scr_y', 'key_x', 'key_y',
               'show_fps','__last_time','writer','fps','following']
    def __init__(self):
        self.planets = []
        self.removed_planets=[]
        self.t = 0
        self.dt = 0.00006 # 速度
        #speed: 程序在绘制一帧之前跳过的帧数
        self.speed=200
        self.scale=1
        self.scr_x=self.key_x=0
        self.scr_y=self.key_y=0
        self.show_fps=True;self.fps=20
        self.writer=Turtle()
        self.writer.hideturtle()
        self.writer.penup()
        self.writer.color("white")
        #following: 跟随某个行星
        self.following=None
    def init(self):
        for p in self.planets:
            p.init()
    def start(self):
        while True:
            self.__last_time=perf_counter()
            # 计算行星的位置
            for _ in range(self.speed):
                self.t += self.dt
                for p in self.planets:
                    p.step()
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
            self.fps=1/(perf_counter()-self.__last_time)

            # 显示帧率
            if self.show_fps:
                self.writer.clear()
                self.writer.goto(
                    scr.window_width()//2-90,scr.window_height()//2-35
                )
                self.writer.write(
                    "fps:%d" % self.fps,
                    font = (None,12)
                )
    def follow(self,planet):
        if self.following:
            self.following.onfollow(False)
        self.following=planet
        self.key_x=self.key_y=0
        planet.onfollow(True)
        scr.ontimer(self.clear_scr, int(1000/self.fps))
    def increase_speed(self,event):
        self.dt+=0.000006
    def decrease_speed(self,event):
        self.dt-=0.000006
    def zoom(self,event):
        if event.keysym=="equal":
            # 放大
            self.scale*=1.33
        else:
            # 缩小
            self.scale/=1.33
        for planet in self.planets:
            scale=planet._size*self.scale
            if planet.keep_on_scr:
                planet.shapesize(max(0.08,scale))
            else:
                planet.shapesize(scale)
        scr.ontimer(self.clear_scr, int(1000/self.fps))
        self.clear_removed_planets()

    def clear_scr(self):
        for planet in self.planets:
            planet.clear()

    def up(self,event=None):
        self.key_y -= 25 / self.scale
        scr.ontimer(self.clear_scr, int(1000/self.fps))
        self.clear_removed_planets()
    def down(self,event=None):
        self.key_y += 25 / self.scale
        scr.ontimer(self.clear_scr, int(1000/self.fps))
        self.clear_removed_planets()
    def left(self,event=None):
        self.key_x += 25 / self.scale
        scr.ontimer(self.clear_scr, int(1000/self.fps))
        self.clear_removed_planets()
    def right(self,event=None):
        self.key_x -= 25 / self.scale
        scr.ontimer(self.clear_scr, int(1000/self.fps))
        self.clear_removed_planets()
    def switchpen(self,x,y):
        targets=[]
        for planet in self.planets:
            psize=max(planet.getsize()*1.375, 2)
            if abs(planet.xcor()-x) <= psize \
               and abs(planet.ycor()-y) <= psize \
               and planet is not self.following:
                targets.append(planet)

            if not planet.has_orbit:
                continue
            if planet.isdown():
                planet.penup()
            else:planet.pendown()
            planet.clear()

        if targets:self.follow(max(targets,key=lambda p:p.m))
        self.clear_removed_planets()

    def clear_removed_planets(self):
        for planet in self.removed_planets:
            planet.clear()
        self.removed_planets=[]

class Star(Turtle):
    def __init__(self, gravSys, m, x, v,
                 shape,shapesize=1,orbit_color=None,has_orbit=True,
                 parent=None,keep_on_scr=False,rotation=None,sun=None):
        Turtle.__init__(self)
        self.shape(shape)
        self._shape=shape
        self._size=shapesize
        self.shapesize(shapesize)
        if orbit_color is not None:
            self.pencolor(orbit_color)
        self.penup()
        self.m = m
        self.x,self.y=x
        self.dx,self.dy=v
        self.setpos(*x)
        self.has_orbit=has_orbit
        self.gravSys = gravSys
        self.keep_on_scr = keep_on_scr
        self.rotation=rotation
        self.sun=sun or (self.gravSys.planets[0] if len(self.gravSys.planets) else None)
        gravSys.planets.append(self)
        self.resizemode("user")
        self.setundobuffer(None)

        self.children=[]
        if parent:
            parent.children.append(self)
    def init(self):
        if self.has_orbit:
            self.pendown()
        dt = self.gravSys.dt
        ax,ay = self.acc()
        self.dx += dt*ax
        self.dy += dt*ay
    def acc(self):
        # ** 计算行星的引力、加速度 **
        ax=ay=0
        for planet in self.gravSys.planets:
            if planet is not self:
                dx=planet.x-self.x
                dy=planet.y-self.y
                try:
                    # 简化前的代码
                    #r = math.hypot(dx,dy)
                    #f = G * self.m * planet.m / r**2
                    # 将力分解为水平、竖直方向的力
                    #ax+=f / self.m * dx / r
                    #ay+=f / self.m * dy / r
                    b = G * planet.m / math.hypot(dx,dy)**3
                    ax+=b * dx
                    ay+=b * dy
                except ZeroDivisionError:pass
        return ax,ay
    def step(self):
        # 计算行星位置
        dt = self.gravSys.dt
        self.x+= dt*self.dx
        self.y+= dt*self.dy

        ax,ay = self.acc()
        self.dx += dt*ax
        self.dy += dt*ay
    def update(self):
        self.setpos((self.x+self.gravSys.scr_x)*self.gravSys.scale,
                    (self.y+self.gravSys.scr_y)*self.gravSys.scale)
        if self.rotation is not None:
            self.left(self.rotation*self.gravSys.dt)
        elif self.sun:
            self.setheading(self.towards(self.sun))
        if abs(self.x)>14000 or abs(self.y)>14000:
            self.gravSys.removed_planets.append(self)
            self.gravSys.planets.remove(self)
            self.hideturtle()
    def getsize(self):
        return self._stretchfactor[0]*PLANET_SIZE*2
    def distance(self,other):
        return math.hypot(self.x-other.x,
                          self.y-other.y)
    def grav(self,other,r=None):
        # 计算两行星间的引力, F = G *m1*m2 / r**2
        if r is None:
            dx=other.x-self.x; dy=other.y-self.y
            r = math.hypot(dx,dy)
        return G * self.m * other.m / r**2
    def tide(self,other,radius=None):
        # 计算行星受到的的潮汐力
        other=other or self.parent
        radius=radius or self.getsize() / 2
        r1=self.distance(other)-radius
        r2=self.distance(other)+radius
        return G *self.m*other.m / r1**2 - \
               G *self.m*other.m / r2**2
    def onfollow(self,arg): # arg:True或False
        for p in self.children:
            p.has_orbit=arg
            if arg and self.isdown():
                p.pendown()
            else:p.penup()
        self.keep_on_scr=True
    def getOrbitSpeed(self,r=None,other=None):
        # 获取某一半径的圆轨道上天体的速率
        # 引力=向心力=m * v**2 / r
        other=other or self.sun
        r=r or self.distance(other)
        return math.sqrt(self.grav(other,r) * r / self.m)
    def getHillSphere(self,other=None):
        # 获取行星希尔球半径
        # 希尔球是环绕在天体（像是行星）周围的空间区域，其中被它吸引的天体受到它的控制，而不是被它绕行的较大天体（像是恒星）所控制。
        other=other or self.sun
        return self.distance(other) * (self.m/other.m/3) ** (1/3)

    def __repr__(self):
        return object.__repr__(self)[:-1] + " shape: %s"%self._shape + '>'

class RoundStar(Star):
    def __init__(self,gravSys, m, x, v,
                 shapesize=1,orbit_color=None,has_orbit=True):
        Star.__init__(self,gravSys, m, x, v,
                     "blank",shapesize,orbit_color,has_orbit,rotation=0)
    def init(self):
        Star.init(self)
        self.setheading=lambda angle:None
    def update(self):
        Star.update(self)
        self.clear()
        size=self.getsize()
        if size>0.04:
            px=3 if size>0.2 else 2
            self.dot(max(size,px))

class Sun(Star):
    # 太阳不移动, 固定在引力系统的中心
    def __init__(self,*args,**kw):
        Star.__init__(self,*args,**kw)
        self.keep_on_scr=True
    def step(self):
        pass
    def update(self):
        self.setpos((self.x+self.gravSys.scr_x)*self.gravSys.scale,
                    (self.y+self.gravSys.scr_y)*self.gravSys.scale)
        if self.rotation is not None:
            self.left(self.rotation*self.gravSys.dt)
        #Star.update(self)

def main():
    global scr
    scr=Screen()
    scr.screensize(10000,10000)
    try:
        scr._canvas.master.state("zoomed")
    except:pass
    scr.bgcolor("black")
    scr.tracer(0,0)

    # create compound turtleshape for planets
    s = Turtle()
    s.reset()
    s.ht()
    s.pu()
    s.fd(PLANET_SIZE)
    s.lt(90)
    s.begin_poly()
    s.circle(PLANET_SIZE, 180,steps=12)
    s.end_poly()
    _light = s.get_poly()
    s.begin_poly()
    s.circle(PLANET_SIZE, 180,steps=12)
    s.end_poly()
    _dark = s.get_poly()
    s.begin_poly()
    s.circle(PLANET_SIZE,steps=12)
    s.end_poly()
    _circle = s.get_poly()
    update()
    s.hideturtle()
    def create_shape(screen,name,light,dark=None): #,gh=False):
        shape = Shape("compound")
        if dark is not None:
            shape.addcomponent(_light,light)
            shape.addcomponent(_dark,dark)
        else:
            shape.addcomponent(_circle,light)
        screen.register_shape(name, shape)

    create_shape(scr,"mercury","gray70","grey50")
    create_shape(scr,"venus","gold","brown")
    create_shape(scr,"earth","blue","blue4")
    create_shape(scr,"moon","gray70","grey30")
    create_shape(scr,"mars","red","red4")
    create_shape(scr,"jupiter","burlywood1","burlywood4")
    create_shape(scr,"saturn","khaki1","khaki4")
    create_shape(scr,"uranus","light blue","blue")
    create_shape(scr,"neptune","blue","dark slate blue")

    # setup gravitational system
    gs = GravSys()
    #SUN_MASS=0
    sun = Sun(gs,SUN_MASS, Vec(0,0), Vec(0,0),
              "circle",1.8,has_orbit=False)
    sun.color("yellow")
    sun.penup()
    # 地球
    earth = Star(gs,EARTH_MASS, Vec(260,0), Vec(0,175.41),
                 "earth",0.8, "blue")
    # 月球
    moon = Star(gs,0, Vec(269,0), Vec(0,232.41),
                "moon",0.4,"gray30", has_orbit=False, parent=earth)

    _scale=1.1139588682
    #_scale=0.8941060808
    moon3 = Star(gs,MOON_MASS, Vec(260,0)*_scale, Vec(0,175.41)*_scale,
                "moon",0.17,"gray30", has_orbit=False, parent=earth)

    # 绑定键盘事件
    cv=scr.getcanvas()
    cv.bind_all("<Key-Up>",gs.up)
    cv.bind_all("<Key-Down>",gs.down)
    cv.bind_all("<Key-Left>",gs.left)
    cv.bind_all("<Key-Right>",gs.right)
    cv.bind_all("<Key-equal>",gs.increase_speed)
    cv.bind_all("<Key-minus>",gs.decrease_speed)
    cv.bind_all("<Control-Key-equal>",gs.zoom) #Ctrl+"+"
    cv.bind_all("<Control-Key-minus>",gs.zoom) #Ctrl+"-"
    #scr.tracer(1,0)
    
    globals().update(locals())
    scr.onclick(gs.switchpen)
    #gs.follow(earth)
    gs.init()
    try:gs.start()
    except (Terminator,TclError):pass

def _test():
    print(moon3.grav(earth))
    print(moon3.tide(sun,moon3.distance(earth)/2))

if __name__ == '__main__':
    main()
    if scr._RUNNING:mainloop()
