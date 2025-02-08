**文章未经作者授权，禁止转载。**
这是一个使用turtle模块的太阳系模拟程序, 模拟天体引力及运行轨道。
运行效果图: 
![运行效果](https://img-blog.csdnimg.cn/f1808a04650e4adaa0fab48df063fe6a.gif#pic_center)

程序使用了多个类, 类GravSys是引力系统, 类Star对应每个行星, 继承自turtle中的Turtle类。
引力公式: `F = G * m1 * m2 / r**2`

项目源代码：[gitcode.net/qfcy_/python-gravity-simulation](https://gitcode.net/qfcy_/python-gravity-simulation)
代码较多, 在下文中将会逐渐讲解。*(抱歉由于是以前发布的文章，使用了旧版的代码)*
@[TOC](目录)
## 1.创建GravSys类
```python
# -*- coding: utf-8 -*-
"""
使用turtle模块的太阳系模拟程序

快捷键:
按Ctrl+“+”或Ctrl+“-”进行缩放。
按↑，↓，←，→键移动。
按“+”或“-”键增加或者降低速度。
单击屏幕开启或关闭轨道显示。
单击行星即可跟随该行星。
拖动鼠标即可发射飞船。

1.2.6版更新: 增加了跟踪飞船，即可按方向键控制飞船功能。
1.3.1版: 增加使用Tab，Shift+Tab键切换行星功能。
1.3.2版: 增加使用pickle模块保存天体数据，及删除天体功能。
1.3.3版: 修复保存天体数据功能的bug，及代码优化。
         增加Ctrl+D键删除所有飞船功能。
"""
try:
    from time import perf_counter
except ImportError:from time import clock as perf_counter # Python 2
from random import randrange
import math,turtle,pickle,os,sys
from turtle import *
try:
    from tkinter import TclError
except ImportError:
    from Tkinter import TclError # Python 2

__version__="1.3.3"

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
        self.scale=1 # 缩放比例
        self.scr_x=self.key_x=0 # scr_x,scr_y:视野的偏移距离
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
        for p in self.planets: # 初始化各个行星
            p.init()
        self.__last_time=perf_counter()
    def start(self): # --主循环, 最关键的函数--
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

    def increase_speed(self,event=None):
        self.dt+=0.0004
    def decrease_speed(self,event=None):
        self.dt-=0.0004

    def switchpen(self): # 隐藏/显示行星轨道
        for planet in self.planets:
            if not planet.has_orbit:
                continue
            if planet.isdown():
                planet.penup()
            else:planet.pendown()
            planet.clear()
    def clear_removed_planets(self): # 清除已移除天体留下的轨道
        for planet in self.removed_planets:
            planet.clear()
        self.removed_planets=[]
    def remove(self,planet): # 移除天体
        self.removed_planets.append(planet)
        self.planets.remove(planet)
        planet._size = 1e-323 # 接近0
        planet.hideturtle()
```
## 2.创建天体、及引力算法
行星部分的`acc()`, `step()`方法是关键, 它提供了计算行星引力及位置、速度的功能。
在上述程序中加入以下代码, 这是使用了万有引力定律的部分: 
```python
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

class Star(Turtle):
    _light=_dark=_circle=None
    def __init__(self, gravSys, name, m, x, v,
                 shapesize=1,has_orbit=True,
                 parent=None,keep_on_scr=False,rotation=None,sun=None,
                 shape=("#b3b3b3","#4d4d4d","gray30")):
        Turtle.__init__(self)
        self.name=name
        self.gs = gravSys
        self._shape=shape
        self._size=shapesize

        self.m = m
        self.x,self.y=x
        self.dx,self.dy=v
        self.ax=self.ay=0
        self.has_orbit=has_orbit
        self.keep_on_scr = keep_on_scr
        self.rotation=rotation
        self.init_shape()
        self.penup()

        self.setpos(self.x,self.y)
        
        self.sun=sun or (self.gs.planets[0]if len(self.gs.planets) else None)
        self.parent=parent or self.sun
        gravSys.planets.append(self)
        self.resizemode("user")
        self.setundobuffer(None)

        self.children=[]
        if parent:
            parent.children.append(self)
    def init(self):
        self.update() # 使行星的turtle移动到初始位置
        self.clear() # 清除轨迹
        if self.has_orbit:
            self.pendown()
    def acc(self):
        # ** 计算行星的引力、加速度 **
        index=self.gs.planets.index(self)
        for i in range(index+1,len(self.gs.planets)):
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
                b = G / math.hypot(dx,dy)**3
                self.ax+=b * dx * planet.m
                self.ay+=b * dy * planet.m
                planet.ax-=b * dx * self.m
                planet.ay-=b * dy * self.m
            except ZeroDivisionError:pass
    def step(self):
        # 计算行星位置
        dt = self.gs.dt
        self.dx += dt*self.ax
        self.dy += dt*self.ay

        self.x+= dt*self.dx
        self.y+= dt*self.dy
    def update(self):
        self.setpos((self.x+self.gs.scr_x)*self.gs.scale,
                    (self.y+self.gs.scr_y)*self.gs.scale)
        if self.rotation is not None:
            self.left(self.rotation*self.gs.dt)
        elif self.sun:
            self.setheading(self.towards(self.sun))
        #if abs(self.x)>14000 or abs(self.y)>14000:
        #    self.gs.remove(self) 清除已飞出太阳系的天体
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

    def __repr__(self):
        return object.__repr__(self)[:-1] + " Name: %s>"%self.name
```
其他的行星类, 继承自类`Star`。类`RoundStar`用于快速绘制简单的圆形天体，类`Sun`对应不移动的太阳。
```python
class RoundStar(Star):
    def __init__(self,gravSys, name, m, x, v,
                 shapesize=1,shape=("blank","gray"),*args,**kw):
        Star.__init__(self,gravSys, name, m, x, v,
                      shapesize,*args,shape=shape,**kw)
    def init(self):
        Star.init(self)
        self.setheading=lambda angle:None
        self._id=None
    def _drawturtle(self):
        # 删除之前绘制的点
        if self._id is not None:
            self.screen._delete(self._id)

        if not self._shown:return # 若已经隐藏
        size=self.getsize()
        if size>0.04:
            px=3 if size>0.2 else 2
            # 绘制形状
            self._id=self.dot(max(size,px))
    def dot(self,size,*color):
        if not color:
            if isinstance(size, (str, tuple)):
                color = self._colorstr(size)
                size = self._pensize + max(self._pensize, 4)
            else:
                color = self._pencolor
                if not size:
                    size = self._pensize + max(self._pensize, 4)
        else:
            if size is None:
                size = self._pensize + max(self._pensize, 4)
            color = self._colorstr(color)
        item = self.screen._dot(self._position, size, color)
        return item

# 修复turtle模块绘制圆点的bug
def _dot(self, pos, size, color):
    dt=size/2
    return self.cv.create_oval(pos[0]-dt,-(pos[1]-dt),
                                pos[0]+dt,-(pos[1]+dt),
                                fill=color,outline=color)
turtle.TurtleScreenBase._dot = _dot

class Sun(Star):
    # 太阳不移动, 固定在引力系统的中心
    def __init__(self,*args,**kw):
        Star.__init__(self,*args,**kw)
        self.keep_on_scr=True
    def acc(self):
        for i in range(1,len(self.gs.planets)):
            planet=self.gs.planets[i]
            dx=planet.x-self.x
            dy=planet.y-self.y
            try:
                b = G * self.m / math.hypot(dx,dy)**3
                planet.ax-=b * dx
                planet.ay-=b * dy
            except ZeroDivisionError:pass
    def step(self):
        pass
    def update(self):
        self.setpos((self.x+self.gs.scr_x)*self.gs.scale,
                    (self.y+self.gs.scr_y)*self.gs.scale)
        if self.rotation is not None:
            self.left(self.rotation*self.gs.dt)
        #Star.update(self)
```
主程序, 实例化天体: 
```python
def main():
    global scr
    scr=Screen()
    scr.screensize(6000,6000)
    try:
        scr._canvas.master.state("zoomed") # 最大化窗口
    except:pass
    scr.bgcolor("black") # 设置背景为黑色
    scr.tracer(0,0) # 禁用turtle自动刷新图形, 加快速度

    # 创建行星
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

    moon = Star(gs,"月球",MOON_MASS, (269,0), (0,268),
                0.5,shape=("#b3b3b3","#4d4d4d","gray30"),
                has_orbit=False, parent=earth)

    mars = Star(gs,"火星",MARS_MASS, (0,430), (-140, 0),
                0.6, shape=("red","#8b0000","red"))
    phobos = Star(gs,"火卫一",PHOBOS_MASS, (0,438), (-167, 0),
                  0.1,shape=('circle',"orange"),
                  has_orbit=False,parent=mars)
    phobos.fillcolor("orange")

    # 创建小行星带
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
```
## 3.为天体设置形状
该部分主要使用turtle的`Shape`类, 该类有`addcomponent`方法。创建形状后, 可调用`screen.register_shape(_name, shape)`方法注册该形状。
在**Star类中**加入以下方法:
```python
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
        # 初始化turtle的行星形状
        # shape表示方式:
        # (亮色, 暗色, [轨道颜色]) (一半亮，一半暗)
        # (颜色,)                 (一个圆)
        # (形状名称, [轨道颜色])   (自定义形状)
        # ()                      (无形状)

        if len(self._shape) == 0:return

        shape = Shape("compound")
        _shape=self._shape;_name=self.name
        if _shape[0] not in scr._shapes:
            # _shape[0]为颜色
            if len(_shape) >= 2: # (亮色, 暗色, [轨道颜色])
                shape.addcomponent(self._light,_shape[0])
                shape.addcomponent(self._dark,_shape[1])
                self.orbit_color = _shape[2] if len(_shape)>=3 else _shape[0]
            else: # (颜色,)
                shape.addcomponent(self._circle,_shape[0])
                self.orbit_color = _shape[0]
                self.color(_shape[0])
            scr.register_shape(_name, shape)
        else:
            # _shape[0]为形状
            _name=_shape[0]
            if len(_shape) >=2:
                self.orbit_color = _shape[1]
                self.color(_shape[1])

        self.shape(_name)
        self.shapesize(self._size)

        self.pencolor(self.orbit_color)
```
## 4.增加放大、移动功能
该功能主要使用gs对象的`dt`,`key_x`,`key_y`,`scale`属性。
在GravSys类中加入以下代码: 
```python
    def zoom(self,scale): # 缩放
        self.scale *= scale
        self._update_size()
        scr.ontimer(self.clear_scr, max(int(1000/self.fps),17)) # 过一段时间后清除旧的行星轨道
        self.clear_removed_planets()
    def _update_size(self):
        for planet in self.planets:
            scale=planet._size*self.scale
            if planet.keep_on_scr or self.following is planet:
                planet.shapesize(max(0.08,scale))
            else:
                planet.shapesize(scale)

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
```
在main函数末尾加入:
```python
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
    gs.init()
    try:gs.start()
    except (Terminator,TclError):pass # 避免用户关闭窗口时引发异常
```
## 5.增加跟随、切换天体的功能
将**GravSys类的start方法**改成下面这样: 
```python
    def start(self):
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
                tip="""fps:%d
放大倍数: %.4f
画面速度: %.4f
""" % (self.fps, self.scale, self.dt)
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
                    scr.window_width()//2-200,scr.window_height()//2-130
                )
                self.writer.write(
                    tip,
                    font = (None,12)
                )
```
在**GravSys类**中加入: 
```python
    def follow(self,planet):
        if self.following:
            self.following.onfollow(False)
        self.following=planet
        self.key_x=self.key_y=0
        planet.onfollow(True)
        scr.ontimer(self.clear_scr, int(1000/self.fps))
# 切换行星
    def _switch(self,dt):
        # 切换到上/下一个行星
        if not self.planets:return # 空列表
        if self.following==None or self.following not in self.planets:
            index=0
        else:
            index=self.planets.index(self.following)+dt
            if index < 0 or index>=len(self.planets):
                index = index % len(self.planets) # 控制index的范围
        self.follow(self.planets[index])
    def switch(self,event=None):
        self._switch(1)
    def reverse_switch(self,event=None):
        self._switch(-1)
    def del_planet(self,event=None): # 删除当前跟踪的行星
        if self.following in self.planets:# if self.following is not None:
            self.remove(self.following)
            if self.following.parent:
                self.follow(self.following.parent)
```
在**Star类**中加入: 
```python
    def onfollow(self,arg): # arg为True时跟随, 为False时表示取消跟随
        for p in self.children:
            p.has_orbit=arg
            if arg and self.isdown():
                p.pendown()
            else:p.penup()
        #self.keep_on_scr=arg
```
## 6.添加发射飞船功能
拖动鼠标时, 程序自动计算飞船位置及速度, 发射飞船。
在主程序加入以下代码: 
```python
SPACECRAFT_MASS = 1
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
        self.shapesize(self.gs.scale)
    def getsize(self):
        return self._stretchfactor[0] * PLANET_SIZE / 2
    def update(self):
        self.setpos((self.x+self.gs.scr_x)*self.gs.scale,
                    (self.y+self.gs.scr_y)*self.gs.scale)
        if self.rotation is not None:
            self.left(self.rotation*self.gs.dt)
        else:
            if self.gs.following:
                if self.gs.following is self:
                    planet=self.parent
                else:planet=self.parent
                if planet is not None:dx=planet.dx;dy=planet.dy
                else:dx=dy=0
            else:dx=dy=0
            angle = math.atan2(self.dy - dy,self.dx - dx) * 180 / math.pi + 90
            self.setheading(angle)
        #if abs(self.x)>14000 or abs(self.y)>14000: # 移除超出范围的飞船
        #    self.gs.removed_planets.append(self)
        #    self.gs.planets.remove(self)
        #    self.hideturtle()

    def accelerate(self):
        v = math.hypot(self.dx,self.dy);step = 400
        # 加速度大小为step, 方向为飞船速度方向
        ax = self.dx / v * step;ay = self.dy / v * step
        self.dx+=ax*self.gs.dt; self.dy+=ay*self.gs.dt
    def slow_down(self):
        v = math.hypot(self.dx,self.dy);step = 400
        # 加速度大小为step, 方向与飞船速度方向相反
        ax = - self.dx / v * step;ay = - self.dy / v * step
        self.dx+=ax*self.gs.dt; self.dy+=ay*self.gs.dt
    def turn_left(self):
        v = math.hypot(self.dx,self.dy);step = 1500
        # 向心加速度与飞船速度方向垂直
        ax = - self.dy / v * step;ay = self.dx / v * step
        self.dx+=ax*self.gs.dt; self.dy+=ay*self.gs.dt
    def turn_right(self):
        v = math.hypot(self.dx,self.dy);step = 1500
        ax = self.dy / v * step;ay = - self.dx / v * step
        self.dx+=ax*self.gs.dt; self.dy+=ay*self.gs.dt
```
在**GravSys类中**加入: 
```python
    def onclick(self,x,y): # 用于处理鼠标单击
        targets=[]
        for planet in self.planets:
            psize=max(planet.getsize()*1.375, 2)
            if abs(planet.xcor()-x) <= psize \
               and abs(planet.ycor()-y) <= psize \
               and planet is not self.following:
                targets.append(planet)

        if targets:self.follow(max(targets,key=lambda p:p.m))
        else:self.switchpen()
        self.clear_removed_planets()

    def _onclick(self,event): # 鼠标按下事件
        x, y = (scr.cv.canvasx(event.x)/scr.xscale,
                -scr.cv.canvasy(event.y)/scr.yscale)
        self.startx,self.starty=x,y
    def _onrelease(self,event): # 鼠标释放事件
        x, y = (scr.cv.canvasx(event.x)/scr.xscale,
                -scr.cv.canvasy(event.y)/scr.yscale)
        if abs(Vec2D(x - self.startx,
                     y - self.starty)) < 9: # 鼠标移动的距离较小
            self.onclick(x,y) # 处理鼠标单击
            return
        # 拖动鼠标时, 自动计算飞船位置及速度, 发射飞船
        x_ = Vec2D(x/self.scale - self.scr_x,
                   y/self.scale - self.scr_y)
        if self.following:
            dx=self.following.dx;dy=self.following.dy
        else:dx=dy=0
        v = Vec2D((x - self.startx)/self.scale + dx,
                  (y - self.starty)/self.scale + dy)
        craft=SpaceCraft(self,SPACECRAFT_MASS,x_,v,parent=self.following)
        craft.penup()
    # 按Ctrl+D键清除所有已发射飞船的功能
    def clear_spacecrafts(self,event=None):
        for p in self.planets.copy(): # copy(): 避免更新self.planets导致循环不全
            if type(p) is SpaceCraft:
                self.remove(p)
        if self.following not in self.planets and \
                    getattr(self.following,"parent",None):
            self.follow(self.following.parent)
```
将原先`GravSys`类的`up`,`down`,`left`,`right`方法**删去**, 改为如下: 

```python
    def up(self,event=None):
        if isinstance(self.following,SpaceCraft):
            self.following.accelerate() # 飞船加速
        else:
            self.key_y -= 25 / self.scale
            scr.ontimer(self.clear_scr, max(int(1000/self.fps),17))
            self.clear_removed_planets()
    def down(self,event=None):
        if isinstance(self.following,SpaceCraft):
            self.following.slow_down() # 飞船减速
        else:
            self.key_y += 25 / self.scale
            scr.ontimer(self.clear_scr, max(int(1000/self.fps),17))
            self.clear_removed_planets()
    def left(self,event=None):
        if isinstance(self.following,SpaceCraft):
            self.following.turn_left() # 飞船左转弯
        else:
            self.key_x += 25 / self.scale
            scr.ontimer(self.clear_scr, max(int(1000/self.fps),17))
            self.clear_removed_planets()
    def right(self,event=None):
        if isinstance(self.following,SpaceCraft):
            self.following.turn_right() # 飞船右转弯
        else:
            self.key_x -= 25 / self.scale
            scr.ontimer(self.clear_scr, max(int(1000/self.fps),17))
            self.clear_removed_planets()
```
## 7.保存程序运行状态 (沙盒)
有时你虽然在程序中创建了飞船, 但无法保存。保存程序运行状态需要用到`pickle`库。
要知道, `pickle`保存一个类的对象时, 会寻找这个对象的`__getstate__`方法, 如果有则调用; 恢复对象时, 则会调用`__setstate__`方法。
**简而言之, `__getstate__`方法把对象的状态交给`pickle`, `__setstate__`方法把pickle储存的对象状态重新交给对象。**
在`GravSys`类加入: 

```python
# 以下函数用于pickle保存状态功能
    def __new__(cls): # 避免pickle中引发AttributeError
        o=super().__new__(cls)
        o.__init__()
        return o
    def __getstate__(self):
        keys = ['t', 'dt', 'speed','scale', 'scr_x', 'scr_y',
               'key_x', 'key_y','show_tip']
        config = {}
        for key in keys:
            config[key]=getattr(self,key)
        if self.following and self.following in self.planets:
            config["following_index"]=self.planets.index(self.following)
        else:
            config["following_index"]=None
        return self.planets, config
    def __setstate__(self,state):
        self.planets=state[0]
        config=state[1]
        index = config.pop("following_index")
        if index is not None:self.following=self.planets[index]
        for key in config:
            setattr(self,key,config[key])
        # 将行星移动到新的大小和位置
        self._update_size()
        for planet in self.planets:
            planet.update()
```
`Star`类加入: 

```python
    def __getstate__(self):
        return (self.gs,self.name,self.m,(self.x,self.y),(self.dx,self.dy),
                self._size,self.has_orbit,self.parent,self.keep_on_scr,self.rotation,
                self.sun,self._shape)
    def __setstate__(self,state):
        self.__init__(*state)
```
`RoundStar`的`__setstate__`方法: 
```python
   # 由于不同类__init__方法参数不同, 因此该方法需要重新编写
   # __setstate__继承自Star类
   def __getstate__(self):
        return (self.gs,self.name,self.m,(self.x,self.y),(self.dx,self.dy),
                self._size,self._shape,self.has_orbit,self.parent,
                self.keep_on_scr,self.rotation,self.sun)
```
`SpaceCraft`类的`__setstate__`方法: 
```python
    def __getstate__(self):
        return (self.gravSys,self.m,(self.x,self.y),(self.dx,self.dy),
                self._size,self.has_orbit,self.parent,self.keep_on_scr,
                self.rotation)
```
主程序改成下面这样: 

```python
FLAG_SAVEFILE = False # 退出时是否自动保存数据到game.pkl
def main():
    # --snip--
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
        gs = GravSys()
        # --snip--
        hw2.color("gray30")

    cv=scr.getcanvas()
    # --snip--

    globals().update(locals()) # 便于程序退出后, 在交互式提示符中调试程序
    gs.init()
    try:gs.start()
    except (Terminator,TclError):pass # 忽略关闭窗口引发的异常
    if FLAG_SAVEFILE or len(sys.argv)==2:
        with open(file,'wb') as f: # 保存数据
            pickle.dump(gs,f)
```
## 7.总结
在程序末尾加入: 
```python
if __name__ == '__main__':
    main()
```
看到这里，记得==点赞==、==收藏==。
项目源代码：[gitcode.net/qfcy_/python-gravity-simulation](https://gitcode.net/qfcy_/python-gravity-simulation)

另外，作者还创建了多个程序的改编版本，放在了上面的源代码中，可以自己看看。
双星系统的模拟：
![](https://img-blog.csdnimg.cn/3b2d5a42810d48fe844f0d28fd975b2a.gif#pic_center =x400)
分子间作用力的**简单**模拟（作者并没有学过专业的分子物理）：
![](https://img-blog.csdnimg.cn/b26fa3a2c5984e9ca2c96a56c9f79fea.gif#pic_center =x400)
*注: 程序灵感来自Python标准库中的turtledemo\planet_and_moon.py*
**声明：本文为作者qfcy的原创文章。==文章未经作者授权，禁止转载。==**

