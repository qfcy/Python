# -*- coding: utf-8 -*-
"""
使用turtle模块的太阳系模拟程序

快捷键:
按Ctrl+“+”或Ctrl+“-”进行缩放。
按↑，↓，←，→键移动。
按“+”或“-”键增加或者降低速度。
单击屏幕开启或关闭轨道显示。
单击行星即可跟随该行星。

1.2.0版: 重写了天体计算部分的代码, 将性能提升至原先的1倍左右。
1.2.04版: 增加了拖动鼠标发射飞船功能。
"""
try:
    from time import perf_counter
# 兼容 Python 2 与 Python 3
except ImportError:from time import clock as perf_counter
from random import randrange
import math,turtle
from turtle import *

try:
    from tkinter import TclError
except ImportError:
    from Tkinter import TclError

__author__="qfcy qq:3076711200"
__email__="3076711200@qq.com"
__version__="1.2.04"

G = 8
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

class GravSys:
    # 引力系统
    __slots__=['planets', 'removed_planets', 't', 'dt', 'speed',
               'scale', 'scr_x', 'scr_y',
               'key_x', 'key_y','startx','starty',
               'show_tip','__last_time','writer','fps','following']
    def __init__(self):
        self.planets = []
        self.removed_planets=[]
        self.t = 0
        self.dt = 0.004 # 速度
        #speed: 程序在绘制一帧之前执行计算的次数
        self.speed=6
        self.scale=1
        self.scr_x=self.key_x=0
        self.scr_y=self.key_y=0
        self.show_tip=True;self.fps=20
        self.writer=Turtle()
        self.writer.hideturtle()
        self.writer.penup()
        self.writer.color("white")

        Star._init_shape()
        #following: 跟随某个行星
        self.following=None
    def init(self):
        for p in self.planets:
            p.init()
        self.__last_time=perf_counter()
    def start(self):
        while True:
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
            self.__last_time=perf_counter()

            # 显示帧率
            if self.show_tip:
                tip="fps:%d" % self.fps
                if self.following:
                    tip+="""
正在跟随: %s
质量: %d""" % (self.following.name,self.following.m)
                    if getattr(self.following,'parent',None):
                        tip+="""
到%s距离: %d""" % (self.following.parent.name,
                self.following.distance(self.following.parent))

                else:
                    tip+='\n\n'

                self.writer.clear()
                self.writer.goto(
                    scr.window_width()//2-160,scr.window_height()//2-80
                )
                self.writer.write(
                    tip,
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
        self.dt+=0.0004
    def decrease_speed(self,event):
        self.dt-=0.0004
    def zoom(self,event):
        if event.keysym=="equal":
            # 放大
            self.scale*=1.33
        else:
            # 缩小
            self.scale/=1.33
        for planet in self.planets:
            scale=planet._size*self.scale
            if planet.keep_on_scr or self.following is planet:
                planet.shapesize(max(0.08,scale))
            else:
                planet.shapesize(scale)
        scr.ontimer(self.clear_scr, max(int(1000/self.fps),17))
        self.clear_removed_planets()

    def clear_scr(self):
        for planet in self.planets:
            planet.clear()

    def up(self,event=None):
        self.key_y -= 25 / self.scale
        scr.ontimer(self.clear_scr, max(int(1000/self.fps),17))
        self.clear_removed_planets()
    def down(self,event=None):
        self.key_y += 25 / self.scale
        scr.ontimer(self.clear_scr, max(int(1000/self.fps),17))
        self.clear_removed_planets()
    def left(self,event=None):
        self.key_x += 25 / self.scale
        scr.ontimer(self.clear_scr, max(int(1000/self.fps),17))
        self.clear_removed_planets()
    def right(self,event=None):
        self.key_x -= 25 / self.scale
        scr.ontimer(self.clear_scr, max(int(1000/self.fps),17))
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

    def onclick(self,event):
        x, y = (scr.cv.canvasx(event.x)/scr.xscale,
                -scr.cv.canvasy(event.y)/scr.yscale)
        # self.switchpen(x,y)
        self.startx,self.starty=x,y
    def onrelease(self,event):
        x, y = (scr.cv.canvasx(event.x)/scr.xscale,
                -scr.cv.canvasy(event.y)/scr.yscale)
        x_ = Vec2D(x/self.scale - self.scr_x,
                   y/self.scale - self.scr_y)
        if self.following:
            dx=self.following.dx;dy=self.following.dy
        else:dx=dy=0
        v = Vec2D((x - self.startx)/self.scale + dx,
                  (y - self.starty)/self.scale + dy)
        
        if abs(Vec2D(x - self.startx,
                     y - self.starty)) < 9:
            self.switchpen(x,y)
            return

        craft=SpaceCraft(self,SPACECRAFT_MASS,x_,v,parent=self.following)
        craft.penup()

class Star(Turtle):
    _light=_dark=_circle=None
    def __init__(self, gravSys, name, m, x, v,
                 shapesize=1,has_orbit=True,
                 parent=None,keep_on_scr=False,rotation=None,sun=None,
                 shape=("#b3b3b3","#4d4d4d","gray30")):
        Turtle.__init__(self)
        self.name=name
        self.gravSys = gravSys
        self._shape=shape
        self._size=shapesize

        self.m = m
        self.x,self.y=x
        self.dx,self.dy=v
        self.has_orbit=has_orbit
        self.keep_on_scr = keep_on_scr
        self.rotation=rotation
        self.init_shape()
        self.penup()

        self.setpos(self.x,self.y)
        
        self.sun=sun or (self.gravSys.planets[0]if len(self.gravSys.planets) else None)
        self.parent=parent or self.sun
        gravSys.planets.append(self)
        self.resizemode("user")
        self.setundobuffer(None)

        self.children=[]
        if parent:
            parent.children.append(self)
    def init(self):
        if self.has_orbit:
            self.pendown()
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
    def getsize(self): # 返回行星的显示大小
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
        #self.keep_on_scr=arg

    @classmethod
    def _init_shape(cls,QUALITY=32):
        if cls._light and cls._dark and cls._circle:return # 已经初始化
        s = Turtle()
        s.reset()
        s.ht()
        s.pu()
        s.fd(PLANET_SIZE)
        s.lt(90)
        s.begin_poly()
        s.circle(PLANET_SIZE, 180,steps=QUALITY//2)
        s.end_poly()
        cls._light = s.get_poly()
        s.begin_poly()
        s.circle(PLANET_SIZE, 180,steps=QUALITY//2)
        s.end_poly()
        cls._dark = s.get_poly()
        s.begin_poly()
        s.circle(PLANET_SIZE,steps=QUALITY)
        s.end_poly()
        cls._circle = s.get_poly()
        update()
        s.hideturtle()
    def init_shape(self):
        # shape表示方式:
        # (亮色, 暗色, [轨道颜色])
        # (颜色,)
        # (形状名称, [轨道颜色])
        # () (无形状)

        if self._shape == ():return

        shape = Shape("compound")
        _shape=self._shape;_name=self.name;_orb_index=2;flag=False
        if _shape[0] not in scr._shapes:
            # _shape[0]为颜色
            if len(_shape) >= 2:
                shape.addcomponent(self._light,_shape[0])
                shape.addcomponent(self._dark,_shape[1])
            else:
                shape.addcomponent(self._circle,_shape[0])
                _orb_index = 0
            flag=True
            scr.register_shape(_name, shape)
        else:
            # _shape[0]为形状
            _name=_shape[0];_orb_index = 1
            if len(_shape) >=2:
                self.color(_shape[1])

        self.shape(_name)
        self.shapesize(self._size)

        if len(_shape)==_orb_index+1:
            self.orbit_color=_shape[_orb_index]
            self.pencolor(self.orbit_color)
        else:
            if flag:
                self.orbit_color=_shape[0]
            else:
                self.orbit_color=self.color()[0]
        self.pencolor(self.orbit_color)
    def __repr__(self):
        return object.__repr__(self)[:-1] + " Name: %s"%self.name + '>'

# 修复turtle模块绘制RoundStar的缺陷
def _dot(self, pos, size, color):
    dt=size/2
    return self.cv.create_oval(pos[0]-dt,-(pos[1]-dt),
                                pos[0]+dt,-(pos[1]+dt),
                                fill=color,outline=color)
turtle.TurtleScreenBase._dot = _dot

class RoundStar(Star):
    def __init__(self,gravSys, name, m, x, v,
                 shapesize=1,shape=("blank","gray"),*args,**kw):
        Star.__init__(self,gravSys, name, m, x, v,
                      shapesize,*args,shape=shape,**kw)
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

class SpaceCraft(Star):
    flag=False;id=0
    def __init__(self, gravSys, m, x, v,
                 shapesize=1,has_orbit=True,
                 parent=None,keep_on_scr=False,rotation=None):
        SpaceCraft.id+=1
        Star.__init__(self, gravSys, 'craft #%d' % SpaceCraft.id,
                 m, x, v,
                 shapesize,has_orbit,
                 parent,keep_on_scr,rotation,shape=())
        self.init()
    @classmethod
    def _init_shape(cls):
        if SpaceCraft.flag:return
        shape = Shape("compound")
        shape.addcomponent(((0,0),(3.333,-6),(0,-4.667)),'#b3b3b3')
        shape.addcomponent(((0,0),(-3.333,-6),(0,-4.667)),'#666666')
        scr.register_shape('craft', shape)
    def init_shape(self):
        self._init_shape()
        self.tilt(-90)
        self.shape('craft')
        self.pencolor('#333333')
        self.shapesize(self.gravSys.scale)
    def getsize(self):
        return self._stretchfactor[0] * PLANET_SIZE / 2
    def update(self):
        self.setpos((self.x+self.gravSys.scr_x)*self.gravSys.scale,
                    (self.y+self.gravSys.scr_y)*self.gravSys.scale)
        if self.rotation is not None:
            self.left(self.rotation*self.gravSys.dt)
        else:
            if self.gravSys.following:
                dx=self.gravSys.following.dx;dy=self.gravSys.following.dy
            else:dx=dy=0
            angle = math.atan2(self.dy - dy,self.dx - dx) * 180 / math.pi + 90
            self.setheading(angle)
        if abs(self.x)>14000 or abs(self.y)>14000:
            self.gravSys.removed_planets.append(self)
            self.gravSys.planets.remove(self)
            self.hideturtle()

def main():
    global scr
    scr=Screen()
    scr.screensize(6000,6000)
    try:
        scr._canvas.master.state("zoomed")
    except:pass
    scr.bgcolor("black")
    scr.tracer(0,0)

    # setup gravitational system
    gs = GravSys()
    sun = Sun(gs,"太阳",SUN_MASS, (0,0), (0,0),
              2.3,has_orbit=False,shape=('yellow',))
    sun.penup()

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
                0.6, shape=("red","#8b0000","red"))
    phobos = Star(gs,"火卫一",PHOBOS_MASS, (0,438), (-167, 0),
                  0.1,shape=('circle',"orange"),
                  has_orbit=False,parent=mars)
    phobos.fillcolor("orange")

    # 创建小行星
    for i in range(10):
        ast=RoundStar(gs,"小行星%d"%i, AST_MASS,(0,0),(0,0),
                      0.05,has_orbit=False)
        ast.setheading(randrange(360))
        ast.forward(randrange(700,800))
        ast.x,ast.y=ast.pos()
        v = ast.pos().rotate(90)
        ast.dx,ast.dy=v[0]/7,v[1]/7
        ast.pu()
        ast.color("gray")

    # 木星及卫星
    jupiter = Star(gs, "木星", JUPITER_MASS, (1100,0), (0, 86),
                   1.2,shape=("#ffd39b","#8b7355","#8b6508"))
    mw1 = Star(gs,"木卫一", MOON_MASS, (1125,0), (0,145),
               0.05, shape=("circle","yellow"),
               has_orbit=False,parent=jupiter)
    mw2 = Star(gs,"木卫二", MOON_MASS, (1142,0), (0,134),
               0.07,shape=("circle","#cd950c"),
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
    hw2.color("gray30")

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
    cv.bind_all("<Control-Key-h>",lambda event:gs.follow(earth))
    cv.bind_all("<Button-1>",gs.onclick)
    cv.bind_all("<B1-ButtonRelease>",gs.onrelease)
    #scr.tracer(1,0)

    gs.init()
    try:gs.start()
    except (Terminator,TclError):pass
    globals().update(locals()) # 便于调试

if __name__ == '__main__':
    main()
    if scr._RUNNING:mainloop()
