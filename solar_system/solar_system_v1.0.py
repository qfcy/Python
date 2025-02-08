#!/usr/bin/env python3
"""
使用turtle模块的太阳系模拟程序

快捷键:
按Ctrl+“+”或Ctrl+“-”进行缩放。
按↑，↓，←，→键移动。
按“+”或“-”键增加或者降低速度。
单击屏幕开启或关闭轨道显示。
"""
from time import perf_counter
from random import randrange
from turtle import Shape, Turtle, update, Screen, Terminator, Vec2D as Vec, mainloop

__author__="qfcy qq:3076711200"
__email__="3076711200@qq.com"
__version__="1.0.3"

G = 8
# 各个行星的质量
SUN_MASS=1000000

MERCURY_MASS=125
VENUS_MASS=3000
EARTH_MASS=4000
MOON_MASS=30
MARS_MASS=600
PHOBOS_MASS=2

JUPITER_MASS=7000
SATURN_MASS=6000
URANUS_MASS=9000
NEPTUNE_MASS=8000

scr=None

class GravSys:
    # 引力系统
    __slots__=['planets', 'removed_planets', 't', 'dt', 'frameskip',
               'scale', 'scr_x', 'scr_y',
               'show_fps','__last_time','writer','fps','following']
    def __init__(self):
        self.planets = []
        self.removed_planets=[]
        self.t = 0
        self.dt = 0.01 # 速度
        #frameskip: 程序在绘制一帧之前跳过的帧数
        self.frameskip=4
        self.scale=1
        self.scr_x=0
        self.scr_y=0
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
                self.scr_x=-self.following._pos[0]
                self.scr_y=-self.following._pos[1]
            # 
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
    def increase_speed(self,event):
        self.dt+=0.001
    def decrease_speed(self,event):
        self.dt-=0.001
    def zoom(self,event):
        if event.keysym=="equal":
            # 放大
            self.scale*=1.33
        else:
            # 缩小
            self.scale/=1.33
        for planet in self.planets:
            planet.shapesize(planet.size*self.scale)
        scr.ontimer(self.clear_scr, int(1000/self.fps))
        
    def clear_scr(self):
        for planet in self.planets:
            planet.clear()

    def up(self,event=None):
        self.scr_y-=50
        scr.ontimer(self.clear_scr, int(1000/self.fps))
    def down(self,event=None):
        self.scr_y+=50
        scr.ontimer(self.clear_scr, int(1000/self.fps))
    def left(self,event=None):
        self.scr_x+=50
        scr.ontimer(self.clear_scr, int(1000/self.fps))
    def right(self,event=None):
        self.scr_x-=50
        scr.ontimer(self.clear_scr, int(1000/self.fps))

class Star(Turtle):
    __slots__=['screen', '_angleOffset', '_angleOrient', '_mode', 'undobuffer', '_fullcircle', '_degreesPerAU', '_position', '_orient', '_resizemode', '_pensize', '_shown', '_pencolor', '_fillcolor', '_drawing', '_speed', '_stretchfactor', '_shearfactor', '_tilt', '_shapetrafo', '_outlinewidth', 'drawingLineItem', 'turtle', '_poly', '_creatingPoly', '_fillitem', '_fillpath', '_hidden_from_screen', 'currentLineItem', 'currentLine', 'items', 'stampItems', '_undobuffersize', 'size', 'm', '_pos', 'v', 'can_switchpen', 'gravSys', 'a']
    def __init__(self, gravSys, m, x, v,
                 shape,shapesize=1,orbit_color=None,can_switchpen=True):
        Turtle.__init__(self)
        self.shape(shape)
        self.size=shapesize
        self.shapesize(shapesize)
        if orbit_color is not None:
            self.pencolor(orbit_color)
        self.penup()
        self.m = m
        self._pos=x
        self.setpos(x)
        self.v = v
        self.can_switchpen=can_switchpen
        gravSys.planets.append(self)
        self.gravSys = gravSys
        self.resizemode("user")
    def init(self):
        if self.can_switchpen:
            self.pendown()
        dt = self.gravSys.dt
        self.a = self.acc()
        self.v = self.v + 0.5*dt*self.a
    def acc(self):
        a = Vec(0,0)
        for planet in self.gravSys.planets:
            if planet is not self:
                v = planet._pos-self._pos
                try:
                    a += (G*planet.m/abs(v)**3)*v
                except ZeroDivisionError:pass
        return a
    def step(self):
        dt = self.gravSys.dt
        self._pos += dt*self.v

        self.a = self.acc()
        self.v = self.v + dt*self.a
    def update(self):
        self.setpos((self._pos+(self.gravSys.scr_x,
                                self.gravSys.scr_y))*self.gravSys.scale)
        if self.size>0.05:
            self.setheading(self.towards(self.gravSys.planets[0]))
        if abs(self._pos[0])>10000 or abs(self._pos[1])>10000:
            self.gravSys.removed_planets.append(self)
            self.gravSys.planets.remove(self)
            self.hideturtle()

class Sun(Star):
    # 太阳不移动, 固定在引力系统的中心
    def step(self):
        pass
    def update(self):
        if self.size*self.gravSys.scale<0.08:
            self.shapesize(0.08)
        self.setpos((self._pos+(self.gravSys.scr_x,
                                self.gravSys.scr_y))*self.gravSys.scale)
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
    s.fd(8)
    s.lt(90)
    s.begin_poly()
    s.circle(8, 180)
    s.end_poly()
    _light = s.get_poly()
    s.begin_poly()
    s.circle(8, 180)
    s.end_poly()
    _dark = s.get_poly()
    s.begin_poly()
    s.circle(8)
    s.end_poly()
    _circle = s.get_poly()
##    _gh=[] # 光环
##    for i in range(4,7,2):
##        s.begin_poly()
##        s.setheading(0)
##        s.setx(i+6)
##        s.setheading(90)
##        s.circle(i+8)
##        s.setheading(0)
##        s.setx(i+7)
##        s.setheading(90)
##        s.circle(i+9)
##        s.end_poly()
##        _gh.append(s.get_poly())
    update()
    s.hideturtle()
    def create_shape(screen,name,light,dark=None): #,gh=False):
        shape = Shape("compound")
        if dark is not None:
            shape.addcomponent(_light,light)
            shape.addcomponent(_dark,dark)
        else:
            shape.addcomponent(_circle,light)
##        if gh:
##            for circ in _gh:
##                shape.addcomponent(circ,dark)
        screen.register_shape(name, shape)
##    def gas_giant_shape(screen,name,light,dark):
##        # create shapes for gas-giant planets


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
    sun = Sun(gs,SUN_MASS, Vec(0,0), Vec(0,0),
              "circle",1.8,can_switchpen=False)
    sun.color("yellow")
    sun.penup()

    # 水星
    mercury = Star(gs,MERCURY_MASS, Vec(60,0), Vec(0,330),
                   "mercury",0.5, "gray30")
    # 金星
    venus = Star(gs,VENUS_MASS, Vec(-130,0), Vec(0,-250),
                 "venus",0.7, "gold4")
    # 地球
    earth = Star(gs,EARTH_MASS, Vec(260,0), Vec(0,173),
                 "earth",0.8, "blue")
    # 月球
    moon = Star(gs,MOON_MASS, Vec(269,0), Vec(0,230),
                "moon",0.5, can_switchpen=False)
    # 火星及卫星
    mars = Star(gs,MARS_MASS, Vec(0,430), Vec(-140, 0),
                "mars",0.6, "red")
    phobos = Star(gs,PHOBOS_MASS, Vec(0,438), Vec(-165, 0),
                  "circle",0.1, "orange", can_switchpen=False)
    phobos.fillcolor("orange")

    # 创建小行星
    for i in range(15):
        ast=Star(gs,100,Vec(0,0),Vec(0,0),
                 "circle",0.05,can_switchpen=False)
        ast.setheading(randrange(360))
        ast.forward(randrange(700,800))
        pos=ast._pos=ast.pos()
        ast.v=Vec(-pos[1]/7, pos[0]/7)
        ast.pu()
        ast.color("gray")

    # 木星及卫星
    jupiter = Star(gs, JUPITER_MASS, Vec(1100,0), Vec(0, 86),
                   "jupiter", 1.2, "darkgoldenrod4")
    mw1 = Star(gs,MOON_MASS, Vec(1125,0), Vec(0,130),
                  "circle",0.05, "yellow", can_switchpen=False)
    mw2 = Star(gs,MOON_MASS, Vec(1145,0), Vec(0,122),
                  "circle",0.07, "darkgoldenrod3", can_switchpen=False)
    # 土星
    saturn = Star(gs, SATURN_MASS, Vec(2200,0), Vec(0, 60),
                  "saturn", 1.0, "khaki4")
    # 天王星
    uranus = Star(gs, URANUS_MASS, Vec(0, 4300), Vec(-43, 0),
                  "uranus", 0.8, "blue")
    # 海王星
    neptune = Star(gs, NEPTUNE_MASS, Vec(7500,0), Vec(0, 34),
                   "neptune", 0.8, "midnight blue")

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
    def switchpen(x=None,y=None):
        for planet in gs.planets+gs.removed_planets:
            if not planet.can_switchpen:
                continue
            if planet.isdown():
                planet.penup()
            else:planet.pendown()
            planet.clear()

    scr.onclick(switchpen)
    #gs.following=earth
    gs.init()
    gs.start()

if __name__ == '__main__':
    main()
    mainloop()
