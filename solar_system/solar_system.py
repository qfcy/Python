# -*- coding: utf-8 -*-
"""
使用tkinter以及turtle模块的太阳系模拟程序。

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
except ImportError:from time import clock as perf_counter # Python 2 (部分支持)
from random import randrange
import math,turtle,pickle,os,sys
from turtle import *
try:
    from tkinter import TclError
except ImportError:
    from Tkinter import TclError # Python 2

__author__="qfcy qq:3076711200"
__email__="3076711200@qq.com"
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

class GravSys:
    # 引力系统
    __slots__=['planets', 'removed_planets', 't', 'dt', 'speed',
               'scale', 'scr_x', 'scr_y', 'G', 'show_orbit',
               'key_x', 'key_y','startx','starty','scr',
               'show_tip','__last_time','writer','pen','fps','following']
    def __init__(self,scr=None):
        self.scr = scr or Screen()
        self.planets = []
        self.removed_planets=[]
        self.G = 8
        self.t = 0
        self.dt = 0.004 # 速度
        #speed: 程序在绘制一帧之前执行计算的次数
        self.speed=6
        self.scale=1 # 缩放比例
        self.scr_x=self.key_x=0 # scr_x,scr_y:视野的偏移距离
        self.scr_y=self.key_y=0
        self.show_tip=True;self.fps=20
        self.show_orbit=True
        self.startx=self.starty=None
        w=self.writer=Turtle()
        w.ht();w.pu();w.color("white")
        p=self.pen=Turtle()
        p.ht();p.pu();p.color("green")

        #following: 跟随某个行星
        self.following=None
    def init(self):
        for p in self.planets: # 初始化各个行星
            p.init()
        self.__last_time=perf_counter()
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
                tip = "fps:%d\n放大倍数: %.4f\n时间速度: %.4f\n" % (
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
    def follow(self,planet):
        self.following=planet
        self.key_x=self.key_y=0
        self.update_pen_state()
        self.scr.ontimer(self.clear_scr, int(1000/self.fps))
    def increase_speed(self,event=None):
        self.dt+=0.0004
    def decrease_speed(self,event=None):
        self.dt-=0.0004
    def _update_size(self):
        for planet in self.planets:
            scale=planet._size*self.scale
            if planet.keep_on_scr or self.following is planet:
                planet.shapesize(max(0.08,scale))
            else:
                planet.shapesize(scale)
    def zoom(self,scale): # 缩放
        self.scale *= scale
        self._update_size()
        self.scr.ontimer(self.clear_scr, max(int(1000/self.fps),17))

    def clear_scr(self):
        for planet in self.planets:
            planet.clear()
        self.clear_removed_planets()

    def up(self,event=None):
        if isinstance(self.following,SpaceCraft):
            self.following.accelerate() # 飞船加速
        else:
            self.key_y -= 25 / self.scale
            self.scr.ontimer(self.clear_scr, max(int(1000/self.fps),17))
    def down(self,event=None):
        if isinstance(self.following,SpaceCraft):
            self.following.slow_down() # 飞船减速
        else:
            self.key_y += 25 / self.scale
            self.scr.ontimer(self.clear_scr, max(int(1000/self.fps),17))
    def left(self,event=None):
        if isinstance(self.following,SpaceCraft):
            self.following.turn_left() # 飞船左转弯
        else:
            self.key_x += 25 / self.scale
            self.scr.ontimer(self.clear_scr, max(int(1000/self.fps),17))
    def right(self,event=None):
        if isinstance(self.following,SpaceCraft):
            self.following.turn_right() # 飞船右转弯
        else:
            self.key_x -= 25 / self.scale
            self.scr.ontimer(self.clear_scr, max(int(1000/self.fps),17))

    def update_pen_state(self): # 更新行星轨道的隐藏和显示
        follow=self.following
        children=getattr(follow,"children",[])
        if self.show_orbit:
            for planet in self.planets:
                planet.clear()
                # 如果跟随的天体不是太阳，则显示其子天体轨道
                if planet.has_orbit or \
                    (not isinstance(follow,Sun)\
                    and planet in children):
                    planet.pendown()
                else:planet.penup()
        else:
            for planet in self.planets:
                planet.clear()
                planet.penup()
    def switchpen(self):
        self.show_orbit=not self.show_orbit
        self.update_pen_state()
    def onclick(self,x,y): # 用于处理鼠标单击
        targets=[]
        for planet in self.planets:
            psize=max(planet.getsize()*1.375, 2)
            if abs(planet.xcor()-x) <= psize \
               and abs(planet.ycor()-y) <= psize \
               and planet is not self.following:
                targets.append(planet)

        if targets:self.follow(max(targets,key=lambda p:p.m))
        else:
            self.switchpen()
            self.clear_removed_planets()

    def _onclick(self,event): # 鼠标按下事件
        scr = self.scr
        x, y = (scr.cv.canvasx(event.x)/scr.xscale,
                -scr.cv.canvasy(event.y)/scr.yscale)
        self.startx,self.starty=x,y
    def _ondrag(self,event): # 鼠标拖曳事件
        scr = self.scr
        scr._canvas.unbind("<B1-Motion>")
        pen = self.pen
        x, y = (scr.cv.canvasx(event.x)/scr.xscale, -scr.cv.canvasy(event.y)/scr.yscale)
        pen.clear()
        if math.hypot(x - self.startx, y - self.starty) >= 9: # 鼠标移动的距离足够大
            pen.goto(self.startx,self.starty)
            pen.dot(3) # 绘制圆点
            pen.pendown()
            pen.goto(x, y) # 绘制线条
            v = math.hypot((x-self.startx)/self.scale, (y-self.starty)/self.scale)
            pen.write("速度: {:.4g}".format(v),font = (None,11))
            pen.penup()
        scr._canvas.bind("<B1-Motion>",self._ondrag)
    def _onrelease(self,event): # 鼠标释放事件
        scr = self.scr
        if self.startx is None or self.starty is None:return
        x, y = (scr.cv.canvasx(event.x)/scr.xscale,
                -scr.cv.canvasy(event.y)/scr.yscale)
        self.pen.clear()
        if math.hypot(x - self.startx,
                      y - self.starty) < 9: # 鼠标移动的距离较小
            self.onclick(x,y) # 处理鼠标单击
            return
        # “发射”飞船
        pos = (self.startx/self.scale - self.scr_x,
               self.starty/self.scale - self.scr_y)
        if self.following: # 加入已跟踪天体的速度
            dx=self.following.dx;dy=self.following.dy
        else:dx=dy=0
        v = ((x - self.startx)/self.scale + dx,
             (y - self.starty)/self.scale + dy)
        ship=SpaceCraft(self,SPACECRAFT_MASS,pos,v,parent=self.following)
        if self.show_orbit:ship.pendown()
        else:ship.penup()
        self.startx=self.starty=None

    def clear_removed_planets(self): # 清除已移除天体留下的轨道
        for planet in self.removed_planets:
            planet.clear()
        self.removed_planets=[]
    def remove(self,planet): # 移除天体
        # 由于需要让天体的轨道保留一段时间，因此这里不调用clear_removed_planets
        self.removed_planets.append(planet)
        self.planets.remove(planet)
        planet._size = 0
        planet.hideturtle()
        parent=planet.parent
        for child in planet.children:
            child.parent=parent # 更新父天体
            if parent:parent.children.append(child)
        for i in range(len(self.planets)): # 更新天体索引
            self.planets[i]._index = i
    def _switch(self,dt):
        # 切换到上/下一个行星
        if not self.planets:return # 空列表
        if self.following is None or self.following not in self.planets:
            index=0
        else:
            index=self.planets.index(self.following)+dt
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
            else:self.following=None
    def clear_spacecrafts(self,event=None):
        for p in self.planets.copy(): # copy(): 避免更新self.planets导致循环不全
            if isinstance(p,SpaceCraft):
                self.remove(p)
        if self.following not in self.planets and \
                    getattr(self.following,"parent",None):
            self.follow(self.following.parent)

    # 以下函数用于pickle保存状态功能
    def __new__(cls,scr=None): # 避免pickle中引发AttributeError
        if scr is None:scr=Screen() # 返回已有的Screen对象
        o=super().__new__(cls)
        o.__init__(scr)
        return o
    def __getstate__(self):
        keys = ['t', 'dt', 'speed','scale', 'scr_x', 'scr_y',
               'key_x', 'key_y','show_tip','G','show_orbit']
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
        # self.sun用于行星、卫星的朝向，self.parent用于标识父天体
        self.sun=sun or (self.gs.planets[0] if len(self.gs.planets) else None)
        self.parent=parent or self.sun

        gravSys.planets.append(self)
        self._index=self.gs.planets.index(self)

        self.orbit_color=None
        self.init_shape()
        self.penup()
        self.setpos(self.x,self.y)
        self.resizemode("user")
        self.setundobuffer(None)

        self.children=[]
        if parent:parent.children.append(self)
        elif self.sun:self.sun.children.append(self)
    def init(self):
        self.update() # 使行星的turtle移动到初始位置
        self.clear() # 清除轨迹
        if self.has_orbit:
            self.pendown()
    def acc(self):
        # ** 计算行星的引力、加速度 **
        G = self.gs.G
        for i in range(self._index+1,len(self.gs.planets)):
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
        #    self.gs.remove(self) # 清除已飞出太阳系的天体
    def getsize(self): # 返回行星的显示大小(直径)
        return self._stretchfactor[0]*PLANET_SIZE*2
    def distance(self,other):
        return math.hypot(self.x-other.x,
                          self.y-other.y)
    def grav(self,other,r=None):
        # 计算两行星间的引力, F = G *m1*m2 / r**2
        if r is None:
            dx=other.x-self.x; dy=other.y-self.y
            r = math.hypot(dx,dy)
        return self.gs.G * self.m * other.m / r**2

    def _init_shape(self,QUALITY=32):
        if Star._light and Star._dark and Star._circle:return # 已经初始化过
        s = Turtle()
        s.ht();s.pu()
        s.fd(PLANET_SIZE)
        s.lt(90)
        s.begin_poly()
        s.circle(PLANET_SIZE, 180,steps=QUALITY//2)
        s.end_poly()
        Star._light = s.get_poly()
        s.begin_poly()
        s.circle(PLANET_SIZE, 180,steps=QUALITY//2)
        s.end_poly()
        Star._dark = s.get_poly()
        s.begin_poly()
        s.circle(PLANET_SIZE,steps=QUALITY)
        s.end_poly()
        Star._circle = s.get_poly()
        s.hideturtle()
    def init_shape(self):
        # 初始化turtle的形状
        # shape表示方式:
        # (亮色, 暗色, [轨道颜色]) (一半亮，一半暗)
        # (颜色,)                 (一个圆)
        # (形状名称, 颜色)        (自定义形状)
        # ()                      (无形状)

        if len(self._shape) == 0:return
        self._init_shape()

        scr = self.gs.scr
        shape = Shape("compound")
        _shape=self._shape;_name=self.name
        if _shape[0] not in scr._shapes:
            # _shape[0]为颜色
            if len(_shape) >= 2: # (亮色, 暗色, [轨道颜色])
                shape.addcomponent(self._light,_shape[0])
                shape.addcomponent(self._dark,_shape[1])
                self.orbit_color = _shape[2] if len(_shape)>=3 else _shape[0] # 无轨道颜色时默认以亮色代替
            else: # (颜色,)
                shape.addcomponent(self._circle,_shape[0])
                self.orbit_color = _shape[0]
                self.color(_shape[0])
            scr.register_shape(_name, shape)
        else:
            # _shape[0]为形状
            _name=_shape[0]
            self.orbit_color = _shape[1]
            self.color(_shape[1])

        self.shape(_name)
        self.shapesize(self._size)

        self.pencolor(self.orbit_color)
    def __repr__(self):
        return object.__repr__(self)[:-1] + " Name: %s>"%self.name
    # 用于pickle模块保存数据
    def __getstate__(self):
        return (self.gs,self.name,self.m,(self.x,self.y),(self.dx,self.dy),
                self._size,self.has_orbit,self.parent,self.keep_on_scr,self.rotation,
                self.sun,self._shape)
    def __setstate__(self,state):
        self.__init__(*state)


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
    def __getstate__(self):
        return (self.gs,self.name,self.m,(self.x,self.y),(self.dx,self.dy),
                self._size,self._shape,self.has_orbit,self.parent,
                self.keep_on_scr,self.rotation,self.sun)

class Sun(Star):
    # 太阳不移动, 固定在引力系统的中心
    def __init__(self,*args,**kw):
        Star.__init__(self,*args,**kw)
        self.keep_on_scr=True
    def acc(self):
        G = self.gs.G
        for i in range(self._index+1,len(self.gs.planets)):
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

class SpaceCraft(Star):
    flag=False;id=0
    def __init__(self, gravSys, m, x, v,
                 shapesize=1,has_orbit=True,
                 parent=None,keep_on_scr=False,rotation=None,name=None):
        SpaceCraft.id+=1
        Star.__init__(self, gravSys, name or 'ship #%d' % SpaceCraft.id,
                 m, x, v,
                 shapesize,has_orbit,
                 parent,keep_on_scr,rotation,shape=())
        self.init()
    def _init_shape(self):
        if SpaceCraft.flag:return
        shape = Shape("compound")
        shape.addcomponent(((0,0),(3.333,-6),(0,-4.667)),'#b3b3b3')
        shape.addcomponent(((0,0),(-3.333,-6),(0,-4.667)),'#666666')
        self.gs.scr.register_shape('craft', shape)
        SpaceCraft.flag=True
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

    def adjust_speed(self,rate):
        # 改变飞船速度，rate为新速度与原速度的比值
        if self.parent:p_dx,p_dy = self.parent.dx, self.parent.dy # 获取父天体速度
        else:p_dx = p_dy = 0
        dx,dy = self.dx-p_dx,self.dy-p_dy # 计算自身相对于父天体的速度
        new_dx,new_dy = dx*rate, dy*rate # 计算新速度
        self.dx,self.dy = new_dx+p_dx,new_dy+p_dy # 更新自身的速度
        d_dx=new_dx-dx # 计算前后速度差值
        d_dy=new_dy-dy
        for child in self.children: # 使子天体获得相同的速度变化量
            child.dx+=d_dx;child.dy+=d_dy
    def accelerate(self): # 飞船加速
        self.adjust_speed(1.01)
    def slow_down(self): # 飞船减速
        self.adjust_speed(1/1.01)
    def turn(self,angle):
        # angle为逆时针的角度，单位为度
        angle = angle * math.pi / 180 # 转换为弧度
        if self.parent:p_dx,p_dy = self.parent.dx, self.parent.dy
        else:p_dx = p_dy = 0
        dx,dy = self.dx-p_dx,self.dy-p_dy
        new_dx,new_dy = dx*math.cos(angle) - dy*math.sin(angle), \
                        dy*math.cos(angle) + dx*math.sin(angle)
        self.dx,self.dy = new_dx+p_dx,new_dy+p_dy
        d_dx = new_dx-dx;d_dy = new_dy-dy
        for child in self.children:
            child.dx+=d_dx;child.dy+=d_dy
    def turn_left(self):
        self.turn(1) # 左(逆时针)转1°
    def turn_right(self):
        self.turn(-1) # 右(顺时针)转1°
    def __getstate__(self):
        return (self.gs,self.m,(self.x,self.y),(self.dx,self.dy),
                self._size,self.has_orbit,self.parent,self.keep_on_scr,
                self.rotation,self.name)

FLAG_SAVEFILE = False # 退出时是否自动保存数据到pickle文件
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
            gs=pickle._load(f)
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
