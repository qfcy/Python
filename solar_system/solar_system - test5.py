# -*- coding: utf-8 -*-
# 黑洞模拟
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
import turtle,math,_thread
from turtle import *
_thread.start_new_thread(lambda:exec("import matplotlib.pyplot as plt",globals()),())

try:
    from PIL import Image,ImageTk
except ImportError:
    Image=None

Vec=Vec2D
try:
    from tkinter import TclError
except ImportError:
    from Tkinter import TclError

__author__="七分诚意 qq:3076711200"
__email__="3416445406@qq.com"
__version__="1.1-test"

G = 8
PLANET_SIZE=8 # 像素
FACTOR=2

# 各个行星的质量
SUN_MASS=1000000

MERCURY_MASS=125
VENUS_MASS=3000
EARTH_MASS=4000
MOON_MASS=30
MARS_MASS=600
PHOBOS_MASS=2
AST_MASS=2

JUPITER_MASS=7000
SATURN_MASS=6000
URANUS_MASS=9000
NEPTUNE_MASS=8000

def _image(self,filename):
    img=Image.open(filename)
    return ImageTk.PhotoImage(img)

def register_shape(self, name, shape=None):
    if shape is None:
        # image
        if name.lower()[-3:] in (".gif","jpg","bmp","png"):
            shape = Shape("image", self._image(name))
        else:
            raise TurtleGraphicsError("Bad arguments for register_shape.\n"
                                      + "Use  help(register_shape)" )
    elif isinstance(shape, tuple):
        shape = Shape("polygon", shape)
    ## else shape assumed to be Shape-instance
    self._shapes[name] = shape

if Image:
    turtle.TurtleScreenBase._image=_image
    turtle.TurtleScreen.register_shape=register_shape

scr=None

class GravSys:
    # 引力系统
    __slots__=['planets', 'removed_planets', 't', 'dt', 'frameskip',
               'scale', 'scr_x', 'scr_y','dt_s','key_x','key_y',
               'show_fps','__last_time','writer','fps','following']
    def __init__(self):
        self.planets = []
        self.removed_planets=[]
        self.t = 0
        self.dt = 0.0005 # 速度
        self.dt_s=100
        #frameskip: 程序在绘制一帧之前跳过的帧数
        self.frameskip=10
        self.scale=1
        self.scr_x=self.key_x=0
        self.scr_y=self.key_y=0
        self.show_fps=True
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
            for _ in range(self.frameskip):
                self.t += self.dt
                for p in self.planets:
                    p.step()
            if self.following!=None:
                self.scr_x=-self.following._pos[0]+self.key_x
                self.scr_y=-self.following._pos[1]+self.key_y
            else:
                self.scr_x=self.key_x
                self.scr_y=self.key_y
            # 
            for p in self.planets:
                p.update()
            #print(tuple(self.planets[1]._pos))
            #self.scale=100/math.hypot(self.planets[1]._pos[0]-self.planets[0]._pos[0],
            #                           self.planets[1]._pos[1]-self.planets[0]._pos[1],)
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
    def increase_speed(self,event):
        self.dt_s*=1.1
    def decrease_speed(self,event):
        self.dt_s/=1.1
    def zoom(self,event):
        if event.keysym=="equal":
            # 放大
            self.scale*=1.8
        else:
            # 缩小
            self.scale/=1.8
        for planet in self.planets:
            planet.shapesize(planet._size*self.scale)
        scr.ontimer(self.clear_scr, max(int(1000/self.fps),17))
        self.clear_removed_planets()

    def clear_scr(self):
        for planet in self.planets:
            planet.clear()

    def up(self,event=None):
        self.key_y -= 40/self.scale
        scr.ontimer(self.clear_scr, max(int(1000/self.fps),17))
        #self.clear_removed_planets()
    def down(self,event=None):
        self.key_y += 40/self.scale
        scr.ontimer(self.clear_scr, max(int(1000/self.fps),17))
        #self.clear_removed_planets()
    def left(self,event=None):
        self.key_x += 40/self.scale
        scr.ontimer(self.clear_scr, max(int(1000/self.fps),17))
        #self.clear_removed_planets()
    def right(self,event=None):
        self.key_x -= 40/self.scale
        scr.ontimer(self.clear_scr, max(int(1000/self.fps),17))
        #self.clear_removed_planets()
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

    def clear_removed_planets(self):pass

l=[]
class Star(Turtle):
    #__slots__=['screen', '_angleOffset', '_angleOrient', '_mode', 'undobuffer', '_fullcircle', '_degreesPerAU', '_position', '_orient', '_resizemode', '_pensize', '_shown', '_pencolor', '_fillcolor', '_drawing', '_speed', '_stretchfactor', '_shearfactor', '_tilt', '_shapetrafo', '_outlinewidth', 'drawingLineItem', 'turtle', '_poly', '_creatingPoly', '_fillitem', '_fillpath', '_hidden_from_screen', 'currentLineItem', 'currentLine', 'items', 'stampItems', '_undobuffersize', 'size', 'm', '_pos', 'v', 'has_orbit', 'gravSys', 'a']
    def __init__(self, gravSys, m, x, v,
                 shape,shapesize=1,orbit_color=None,has_orbit=True,parent=None,
                 rotation=None,sun=None):
        Turtle.__init__(self)
        self.shape(shape)
        self._shape=shape
        self._size=shapesize
        self.shapesize(shapesize)
        if orbit_color is not None:
            self.pencolor(orbit_color)
        self.penup()
        self.m = m
        #print(type(x))
        self._pos=x
        self.setpos(x)
        self.v = v
        self.has_orbit=has_orbit
        gravSys.planets.append(self)
        self.gravSys = gravSys
        self.rotation=rotation
        self.sun=sun or (self.gravSys.planets[0] if len(self.gravSys.planets) else None)
        self.resizemode("user")

        self.children=[]
        if parent:
            parent.children.append(self)
    def init(self):
        if self.has_orbit:
            self.pendown()
        dt = self.gravSys.dt
        self.a = self.acc()
        self.v = self.v + 0.5*dt*self.a
    def acc(self):
        a = Vec(0,0)
        for planet in self.gravSys.planets:
            if planet is not self:
                v = planet._pos-self._pos
                self.d=math.sqrt(v[0]**2+v[1]**2)
                l.append(self.d)
                #if self.d<=0.62:
                    #print('Dropped')
                try:
                    a += (G*planet.m/abs(v)**3)*v#*pow(d,0.2)
                except ZeroDivisionError:
                    print('dropped') #raise
                    #self.gravSys.scale=1e108
        return a
    def step(self):
        dt = self.gravSys.dt
        self._pos += dt*self.v

        a = self.acc()
        MAX=400
##        self.v = Vec(max(min(self.v[0] + dt*a[0],MAX),-MAX),
##                     max(min(self.v[1] + dt*a[1],MAX),-MAX))# - Vec(2*dt,2*dt)
        self.v = self.v + dt*a
        self.gravSys.dt=1/math.hypot(*self.v)**2.5*self.gravSys.dt_s
        speed=100/math.hypot(*self.v)
        self.v*=pow(speed,max(dt,0.00004))
    def update(self):
        self.setpos((self._pos+(self.gravSys.scr_x,
                                self.gravSys.scr_y))*self.gravSys.scale)
        if self.rotation is not None:
            self.left(self.rotation*self.gravSys.dt)
        elif self.sun:
            self.setheading(self.towards(self.sun))
    def getsize(self):
        return self._stretchfactor[0]*PLANET_SIZE*FACTOR
    def distance(self,other):
        return math.hypot(self._pos[0]-other._pos[0],
                          self._pos[1]-other._pos[1])
    def grav(self,other):
        # 计算两行星间的引力, F = G *m1*m2 / r**2
        r=math.hypot(self._pos[0]-other._pos[0],
                     self._pos[1]-other._pos[1])
        return G *self.m*other.m / r**2
    def tide(self,other,radius=None):
        # 计算行星对自身的潮汐力
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

class Sun(Star):
    # 太阳不移动, 固定在引力系统的中心
    def step(self):
        pass
    def update(self):
        if self._size*self.gravSys.scale<0.08:
            self.shapesize(0.08)
        Star.update(self)

class RoundStar(Star):
    def __init__(self,gravSys, m, x, v,
                 shapesize=1,orbit_color=None,has_orbit=True):
        Star.__init__(self,gravSys, m, x, v,
                     "blank",shapesize,orbit_color,has_orbit)
    def update(self):
        Star.update(self)
        self.clear()
        size=self.getsize()
        if size>0.04:
            px=3 if size>0.2 else 2
            self.dot(max(size,px))

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
    def create_shape(screen,name,light,dark=None):
        shape = Shape("compound")
        if dark is not None:
            shape.addcomponent(_light,light)
            shape.addcomponent(_dark,dark)
        else:
            shape.addcomponent(_circle,light)
        screen.register_shape(name, shape)


    create_shape(scr,"earth","blue","blue4")
    try:scr.register_shape('bh.png')
    except (turtle.TurtleGraphicsError,OSError):pass

    # setup gravitational system
    gs = GravSys()
    sun = Sun(gs,SUN_MASS, Vec(0,0), Vec(0,0),
              "circle",0.3,"yellow",has_orbit=False)
    #sun.color("yellow")
    sun.penup()

    # 地球
    earth = Star(gs,EARTH_MASS, Vec(260,0), Vec(0,173),
                 "earth",0.21, "blue")

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
    #scr.tracer(1,0)
    

    scr.onclick(gs.switchpen)
    #gs.follow(earth)
    gs.scale=1.5
    gs.init()
    try:gs.start()
    except (Terminator,TclError):pass
    finally:
        globals().update(locals())
        plt.plot(range(len(l)),l)
        plt.show()

if __name__ == '__main__':
    main()
    if scr._RUNNING:mainloop()
