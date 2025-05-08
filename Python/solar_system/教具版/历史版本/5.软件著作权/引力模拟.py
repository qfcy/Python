# -*- coding: utf-8 -*-
"""快捷键:
按Ctrl+“+”或Ctrl+“-”进行缩放。
按↑，↓，←，→键移动。
按“+”或“-”键增加或者降低速度。
单击屏幕开启或关闭轨道显示。
单击行星即可跟随该行星。
拖动鼠标即可发射飞船。

更多帮助，详见“操作说明文档”这一文件。
"""
from time import perf_counter
from random import randrange
import math,turtle,pickle,os,sys,warnings
from turtle import *
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as msgbox
import tkinter.filedialog as filediag

import pandas as pd

__version__="1.3.3"

PLANET_SIZE=8 # 天体大小为1时的半径(像素)

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

def get_floating_point_precision(num):
    # 返回num该处浮点数的精度(以2的对数)
    return math.floor(math.log2(abs(num))-52) # 如果是单精度浮点数，则52要改为23
def calc_angle(center,cur,next):
    # 计算天体扫过角度(返回单位为度)。参数center为中心，cur为当前位置，next为下一个位置
    # 计算三角形三条边的长度
    a = math.hypot(center[0]-cur[0],center[1]-cur[1]) # 中心到当前位置
    b = math.hypot(center[0]-next[0],center[1]-next[1]) # 中心到下一位置
    c = math.hypot(next[0]-cur[0],next[1]-cur[1]) # 当前位置到下一位置
    if a==0 or b==0 or c==0:return 0 # 避免ZeroDivisionError
    else:
        try:return math.acos((a**2+b**2-c**2)/(2*a*b)) * 180 / math.pi # 余弦定理
        except ValueError:return 0 # 天体坐标极大时，会发生 ValueError: math domain error

class GravSys:
    # 引力系统
    __slots__=['planets', 'removed_planets', 't', 'dt', 'speed','show_orbit',
               'scale', 'scr_x', 'scr_y', 'G','enable_accelerate','enable_collision',
               'key_x', 'key_y','startx','starty','calc_time','elasticity','show_label',
               'show_tip','__last_time','writer','pen','fps','following']
    def __init__(self):
        self.planets = []
        self.removed_planets=[]
        self.G = 8
        self.t = 0
        self.dt = 0.00006 # 时间速度，每次计算经过的时间
        #speed: 画面速度，程序在绘制一帧之前执行计算的次数
        self.speed=340
        self.scale=1 # 缩放比例
        self.scr_x=self.key_x=0 # scr_x,scr_y:视野的偏移距离
        self.scr_y=self.key_y=0
        self.show_tip=1;self.fps=20
        self.calc_time=0;self.elasticity=0.9
        self.enable_accelerate = True
        self.enable_collision = False
        self.show_orbit = True
        self.show_label = False
        self.startx=self.starty=None
        w=self.writer=Turtle()
        w.ht();w.pu();w.color("white")
        p=self.pen=Turtle()
        p.ht();p.pu();p.color("green")

        Star._init_shape()
        #following: 跟随某个行星
        self.following=None
    def init(self):
        for p in self.planets: # 初始化各个行星
            p.init()
        self.__last_time=perf_counter()
    def start(self): # 主循环, 最关键的函数
        for i in range(len(self.planets)):
            p=self.planets[i]
            if isinstance(p,Sun):
                sun_index=i;break
        else:sun_index=-1
        while True:
            calc_starttime=perf_counter()
            # 计算行星的位置
            if self.enable_accelerate:
                self.t += self.dt * self.speed
                # 计算行星的位置,使用numba库加速
                lst=[]
                for p in self.planets:
                    lst.extend([p.m,p.x,p.y,p.dx,p.dy,0.0,0.0])
                lst = _acc_numba(self.speed,float(self.G),float(self.dt),lst,sun_index)
                for i in range(0,len(lst),7):
                    p=self.planets[i//7]
                    p.m,p.x,p.y,p.dx,p.dy,*_=lst[i:i+7]
            else:
                for _ in range(self.speed):
                    self.t += self.dt
                    for p in self.planets: # 计算各行星加速度
                        p.acc()
                    for p in self.planets: # 计算速度、位移
                        p.step()
                    if self.enable_collision:
                        for p in self.planets: # 计算碰撞
                            p.check_collision()
                    for p in self.planets:
                        p.ax=p.ay=0

            self.calc_time=perf_counter()-calc_starttime

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
            if self.show_tip != 0:
                if self.show_tip==1: # 简明
                    tip = self.brief_info()
                    left_border=205
                else:
                    tip = self.detailed_info()
                    left_border=410
                top_h=26;fontsize=12
                h = (tip.count("\n")+1)*(fontsize*3-4)/2 + top_h # 3和4为调试中推出的数值
                self.writer.clear()
                self.writer.goto(
                    scr.window_width()//2-left_border,scr.window_height()//2-h
                )
                self.writer.write(
                    tip,
                    font = (None,fontsize)
                )
            else:self.writer.clear()
    def brief_info(self):
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
            tip += self.status_info()
            tip += "\n\n提示: 按F3键可查看更详\n      细的天体信息。"
        else:tip+=self.status_info()
        return tip
    def detailed_info(self):
        tip = "fps:{:.0f}\n放大倍数: {:.10g}\n".format(self.fps, self.scale)
        tip += "时间: {:#.12g}\t时间速度: {:#.6f}\n".format(self.t, self.dt)
        if self.following:
            follow = self.following
            tip += "\n正在跟随: {}\n质量: {:.10g}".format(follow.name,follow.m)
            if getattr(follow,'parent',None):
                tip+="\n到{}距离: {}".format(follow.parent.name,
                        follow.distance(follow.parent))
                center = (follow.parent.x,follow.parent.y)
                # 计算天体相对父天体速度
                dx,dy = follow.dx-follow.parent.dx, \
                        follow.dy-follow.parent.dy
            else:
                center = (0,0)
                dx,dy = follow.dx, follow.dy

            x, y = follow.x, follow.y
            tip+="\n坐标: ({:.16g}, {:.16g})".format(x,y)
            tip+="\n(相对)速度: ({:.10g}, {:.10g})".format(dx,dy)
            tip+="\n\t    ({:.16g})\t角度: {:.4f}°".format(
                math.hypot(dx,dy), math.atan2(dy,dx)/math.pi*180)
            tip+="\n所受引力合力: {:.10g}".format(follow.calc_acc()*follow.m)
            if follow.parent:
                ecc, semimajor_axis, angle_peri=follow.calc_orbit()
                tip+="\n轨道离心率: {:.5g}\t半长轴: {:.8g}".format(ecc,semimajor_axis)
                tip+="\n近日点与水平方向夹角: {:.4f}°".format(angle_peri)

            dx_s, dy_s = dx*self.dt, dy*self.dt
            next_x, next_y = x+dx_s, y+dy_s
            tip+="\n"
            tip+="\n单次计算(相对)位移：({:.8g},{:.8g})".format(dx_s,dy_s)
            # 天体相对父天体公转的角度
            tip+="\n单次计算角度误差：{:.8g}°".format(calc_angle(center,(x,y),(next_x,next_y)))
            if not (x==0 or y==0):
                prec_x=get_floating_point_precision(x)
                prec_y=get_floating_point_precision(y)
                # 倍数为单次计算位移与浮点数精度之比
                tip+="\n浮点数精度误差：x:2^{}({:.4g}倍),\n\t\ty:2^{}({:.4g}倍)".format(
                    prec_x, abs(dx_s)/2**prec_x, prec_y, abs(dy_s)/2**prec_y)

            # 程序运行中需要计算和渲染，这是单次循环中计算时间占总运行时间的比例
            tip+="\n\n计算时间占运行时间比例：{:.4g}%".format(self.calc_time/(1/self.fps)*100)
            tip+=self.status_info(False)
            tip+="\n\n提示:可按住下方滚动条暂停模拟，更好地查看数据。"
        else:tip+=self.status_info()
        return tip
    def status_info(self,multiline=True):
        tip="\n" if multiline else ""
        tip+="\n硬件加速已启用" if self.enable_accelerate else "\n硬件加速已禁用"
        tip+="\n" if multiline else " "
        tip+="碰撞已启用 弹性:%.4f"%self.elasticity if self.enable_collision else "碰撞已禁用"
        return tip
    def follow(self,planet):
        self.following=planet
        self.key_x=self.key_y=0
        self.update_pen_state()
        scr.ontimer(self.clear_scr, int(1000/self.fps))
    def increase_speed(self,event=None):
        if self.enable_accelerate:
            self.dt+=0.000006
        else:self.dt+=0.0004
    def decrease_speed(self,event=None):
        if self.enable_accelerate:
            self.dt-=0.000006
        else:self.dt-=0.0004
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
        scr.ontimer(self.clear_scr, max(int(1000/self.fps),17))

    def clear_scr(self):
        for planet in self.planets:
            planet.clear()
        self.clear_removed_planets()

    def up(self,event=None):
        if isinstance(self.following,SpaceCraft):
            self.following.accelerate() # 飞船加速
        else:
            self.key_y -= 25 / self.scale
            scr.ontimer(self.clear_scr, max(int(1000/self.fps),17))
    def down(self,event=None):
        if isinstance(self.following,SpaceCraft):
            self.following.slow_down() # 飞船减速
        else:
            self.key_y += 25 / self.scale
            scr.ontimer(self.clear_scr, max(int(1000/self.fps),17))
    def left(self,event=None):
        if isinstance(self.following,SpaceCraft):
            self.following.turn_left() # 飞船左转弯
        else:
            self.key_x += 25 / self.scale
            scr.ontimer(self.clear_scr, max(int(1000/self.fps),17))
    def right(self,event=None):
        if isinstance(self.following,SpaceCraft):
            self.following.turn_right() # 飞船右转弯
        else:
            self.key_x -= 25 / self.scale
            scr.ontimer(self.clear_scr, max(int(1000/self.fps),17))

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
        x, y = (scr.cv.canvasx(event.x)/scr.xscale,
                -scr.cv.canvasy(event.y)/scr.yscale)
        self.startx,self.starty=x,y
    def _ondrag(self,event): # 鼠标拖曳事件
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
            if type(p) is SpaceCraft:
                self.remove(p)
        if self.following not in self.planets and \
                    getattr(self.following,"parent",None):
            self.follow(self.following.parent)

    # 以下函数用于pickle保存状态功能
    def __new__(cls): # 避免pickle中引发AttributeError
        o=super().__new__(cls)
        o.__init__()
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

# ----------------------应用numba模块提高速度--------------------------------
# lst的每7项分别是一个天体的质量，x、y坐标，x、y速度和x、y加速度
# 由于numba库不支持二维数组，也就是列表映射(List Reflection)，就使用一维数组代替
def _acc_numba(steps,G,dt,lst,sun_index):
    for _ in range(steps):
        # 计算加速度
        index=sun_index*7
        for i in range(0,len(lst),7):
            for j in range(i+7,len(lst),7):
                dx=lst[j+1]-lst[i+1]
                dy=lst[j+2]-lst[i+2]

                if not (dx==0 and dy==0): # 忽略除零的异常
                    b = G / math.hypot(dx,dy)**3
                    if sun_index==-1 or i!=index: # 太阳不移动
                        lst[i+5]+=b * dx * lst[j+0]
                        lst[i+6]+=b * dy * lst[j+0]
                    lst[j+5]-=b * dx * lst[i+0]
                    lst[j+6]-=b * dy * lst[i+0]
        # 计算新的速度和位置
        for i in range(0,len(lst),7):
            lst[i+3] += dt*lst[i+5]
            lst[i+4] += dt*lst[i+6]
            lst[i+5]=lst[i+6]=0

            lst[i+1] += dt*lst[i+3]
            lst[i+2] += dt*lst[i+4]
    return lst

try:
    # 使用更快的C语言编译成的pyd文件提升速度
    from solar_system_accelerate_util import accelerate as _acc_numba
except ImportError:
    warnings.warn("Failed to import module solar_system_accelerate_util, using module numba instead.")
    from numba import jit
    _acc_numba = jit(nopython=True)(_acc_numba) # 相当于 @jit(nopython=True)
#--------------------------------------------------------------------------------

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
        w=self.writer=Turtle()
        w.ht();w.pu();w.color("white")

        self.children=[]
        if parent:parent.children.append(self)
        elif self.sun:self.sun.children.append(self)
    def init(self):
        self.update() # 使行星的turtle移动到初始位置
        self.clear() # 清除轨迹
        self.m=float(self.m);self.x=float(self.x);self.y=float(self.y)
        self.dx=float(self.dx);self.dy=float(self.dy)
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
        if self.gs.show_label:self.show_label()
        else:self.writer.clear()
        #if abs(self.x)>14000 or abs(self.y)>14000:
        #    self.gs.remove(self) # 清除已飞出太阳系的天体
    def check_collision(self):
        # 碰撞检测（备用的函数）
        for planet in self.gs.planets:
            if planet is self:continue
            if self.hit(planet):
                m1=self.m;m2=planet.m
                adx=(self.dx+planet.dx)/2
                ady=(self.dy+planet.dy)/2
                dx1 = (m1-m2)/(m1+m2)*self.dx + 2*m2/(m2+m1)*planet.dx
                dy1 = (m1-m2)/(m1+m2)*self.dy + 2*m2/(m2+m1)*planet.dy
                dx2 = (m2-m1)/(m1+m2)*planet.dx + 2*m1/(m2+m1)*self.dx
                dy2 = (m2-m1)/(m1+m2)*planet.dy + 2*m1/(m2+m1)*self.dy
                rate = self.gs.elasticity # 碰撞的"弹性", 0为完全非弹性碰撞, 1为弹性碰撞
                self.dx=dx1*rate+adx*(1-rate)
                self.dy=dy1*rate+ady*(1-rate)
                planet.dx=dx2*rate+adx*(1-rate)
                planet.dy=dy2*rate+ady*(1-rate)

                dx=planet.x-self.x;dy=planet.y-self.y
                dis=math.hypot(dx,dy)
                newdis=(self._size + planet._size) * PLANET_SIZE
                self.x=planet.x-(dx*newdis/dis+dx)/2
                self.y=planet.y-(dy*newdis/dis+dy)/2
                planet.x=self.x+(dx*newdis/dis+dx)/2
                planet.y=self.y+(dy*newdis/dis+dy)/2
    def hit(self,other): # 新增
        return self.distance(other) < \
               self._size * PLANET_SIZE + other._size * PLANET_SIZE
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
    def calc_acc(self):
        # 计算自身加速度大小并返回
        G = self.gs.G; ax=ay=0
        for planet in self.gs.planets:
            dx=planet.x-self.x
            dy=planet.y-self.y
            try:
                b = G / math.hypot(dx,dy)**3
                ax+=b * dx * planet.m
                ay+=b * dy * planet.m
            except ZeroDivisionError:pass
        return math.hypot(ax,ay)
    def calc_orbit(self): # 计算轨道参数
        if self.parent is None:
            raise ValueError("Celestial Body %s has no parent"%self.name)
        else:parent=self.parent
        # 计算相对位置矢量和相对速度矢量
        dx, dy = self.x - parent.x, self.y - parent.y
        vx, vy = self.dx - parent.dx, self.dy - parent.dy
        r = math.hypot(dx, dy)
        v = math.hypot(vx, vy)

        mu = self.gs.G * (parent.m + self.m)
        ecc_vec = ((v ** 2 - mu / r) * dx - (dx * vx + dy * vy) * vx,
                   (v ** 2 - mu / r) * dy - (dx * vx + dy * vy) * vy)

        ecc = math.hypot(ecc_vec[0], ecc_vec[1]) / mu
        semimajor_axis = 1 / (2 / r - v ** 2 / mu)
        #pos_peri = ((a * (1 - ecc)) * ecc_vec[0] / ecc, (a * (1 - ecc)) * ecc_vec[1] / ecc) # 近日点坐标
        angle_peri = math.atan2(ecc_vec[1], ecc_vec[0]) % (math.pi*2) / math.pi*180
        return ecc, semimajor_axis, angle_peri
    def getOrbitSpeed(self,r=None,other=None):
        # 获取某一半径的圆轨道上天体的速率
        # 引力=向心力=m * v**2 / r
        other=other or self.sun
        r=r or self.distance(other)
        return math.sqrt(self.grav(other,r) * r / self.m)
    def getHillSphere(self,other=None):
        # 获取行星希尔球半径（备用的函数）
        # 希尔球是环绕在天体（像是行星）周围的空间区域，其中被它吸引的天体受到它的控制，而不是被它绕行的较大天体（像是恒星）所控制。
        other=other or self.parent
        return self.distance(other) * (self.m/(other.m*3)) ** (1/3)

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
        s.hideturtle()
    def init_shape(self):
        # 初始化turtle的形状
        # shape表示方式:
        # (亮色, 暗色, [轨道颜色]) (一半亮，一半暗)
        # (颜色,)                 (一个圆)
        # (形状名称, 颜色)        (自定义形状)
        # ()                      (无形状)

        if len(self._shape) == 0:return

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
    def show_label(self):
        self.writer.clear()
        self.writer.setpos(*self.pos())
        self.writer.write(self.name,font=(None,10))
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
        if self.gs.show_label:self.show_label()
        else:self.writer.clear()
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
        if self.gs.show_label:self.show_label()
        else:self.writer.clear()
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


# 避免eval()函数产生安全漏洞
globals_ = globals()
def _safe_eval(value):
    if value in globals_:
        return globals_[value] # 从全局变量中直接取出
    else:
        dct = {"__builtins__":{}, # 不允许调用内置函数
                "TRUE":True,"FALSE":False} # 允许使用Excel中"TRUE"和"FALSE"的数据
        return _old_eval(value,dct)
_old_eval=eval
eval=_safe_eval

# tkinter 界面部分
def find_planet(gs,name):
    for planet in gs.planets:
        if planet.name==name:
            return planet
    return None
def clear_old_planets():
    for planet in gs.planets: # 清除旧行星
        planet.clear()
        planet.hideturtle()
    gs.planets.clear()
def load_file(filename):
    table = str.maketrans("（），。“”【】",'(),.""[]') # 用于将用户输入的中文标点转换为英文标点
    following_planet=None
    try:
        if filename.lower().endswith(".xlsx"):
            df=pd.read_excel(filename,dtype=str,sheet_name="Celestial Bodies")
            conf=pd.read_excel(filename,dtype=str,sheet_name="Config")
            for col in conf: # 读取配置
                if col != "following":
                    setattr(gs,col,eval(conf[col][0]))
                else:
                    following_planet=conf[col][0] # 跟踪的天体
        elif filename.lower().endswith(".pkl"):
            with open(filename,'rb') as f:
                new_gs=pickle.load(f)
                gs.writer.clear() # 清除旧的提示文字
                clear_old_planets()
                gs.planets.extend(new_gs.planets)
                for planet in gs.planets:
                    planet.gs=gs
                for attr in new_gs.__slots__:
                    # 更新新的gs对象的属性
                    try:setattr(gs,attr,getattr(new_gs,attr))
                    except AttributeError:pass
                gs.init() # 初始化
                return
        else:
            df=pd.read_csv(filename,dtype=str)
    except Exception as err:
        msgbox.showinfo("","读取文件%s时出错。(%s:%s)"%(filename,type(err).__name__,str(err)))
        return

    clear_old_planets()
    gs.scr_x=gs.key_x=0
    gs.scr_y=gs.key_y=0

    for i in range(len(df)):
        try:
            line = df.loc[i] # 取出一行数据,line为Series类型
            kwargs={} # 初始化天体用的参数
            # 取出天体的各个参数
            for key in line.index:
                value = line[key] # values为Series类型
                if str(value)=="nan": # 空值
                    continue
                value = value.translate(table) # 转为英文标点
                if key in ("name","parent","sun"):
                    kwargs[key] = value # 直接用字符串作为值
                else:kwargs[key] = eval(value)
                
            if kwargs == {}:
                continue # 忽略表格中的空行

            # 取出天体所属的类
            star_type = kwargs["type"]
            del kwargs["type"]
            # 取出天体的卫星及所属恒星
            if "parent" in kwargs:
                parent=find_planet(gs,kwargs["parent"])
                if parent is None:
                    msgbox.showinfo("","没有找到天体 %s 的父天体，请修改您的天体列表。"%kwargs["name"])
                    del kwargs["parent"]
                else:
                    kwargs["parent"]=parent
            if "sun" in kwargs:
                sun=find_planet(gs,kwargs["sun"])
                if sun is None:
                    msgbox.showinfo("","没有找到天体 %s 对应的恒星，请修改您的天体列表。"%kwargs["name"])
                    del kwargs["sun"]
                else:
                    kwargs["sun"]=sun
            star_type(gs,**kwargs) # 初始化天体实例
        except Exception as err:
                # 显示错误信息
                msgbox.showinfo("","读取表格第 %d 行 %s 列出错，请修改您的天体列表。\n%s: %s" % (
                                i+1+1, key,type(err).__name__,str(err)))
    gs.following=find_planet(gs,following_planet)
    gs.zoom(1)
    gs.init()
def save(filename):
    df=pd.DataFrame(columns=["name","m","x","v","shapesize","shape",
                            "type","has_orbit","parent","keep_on_scr",
                            "rotation","sun"])
    for planet in gs.planets:
        parent_name=getattr(planet.parent,"name",None)
        sun_name=getattr(planet.sun,"name",None)
        if isinstance(planet,SpaceCraft):sun_name=None # 飞船不支持shape和sun参数
        shape=planet._shape if not isinstance(planet,SpaceCraft) else None
        data = [planet.name,planet.m,(planet.x,planet.y),(planet.dx,planet.dy),
                planet._size,shape,type(planet).__name__,planet.has_orbit,
                parent_name,planet.keep_on_scr,planet.rotation,sun_name]
        data = [str(d) if d is not None else "" for d in data]
        df.loc[len(df)] = data
    try:
        if filename.lower().endswith(".xlsx"):
            # 保存gs对象的配置
            attr_list=["t","dt","speed","scale","G","show_tip","show_orbit","show_label"]
            conf=pd.DataFrame(columns=attr_list)
            for attr in attr_list:
                conf[attr] = [str(getattr(gs,attr))]
            conf["following"] = getattr(gs.following,"name",None) or ''
            with pd.ExcelWriter(filename) as w:
                df.to_excel(w,sheet_name="Celestial Bodies",index=False) # 不保存索引
                conf.to_excel(w,sheet_name="Config",index=False)
        elif filename.lower().endswith(".pkl"):
            with open(filename,'wb') as f: # 保存pickle数据
                pickle.dump(gs,f)
        else:
            df.to_csv(filename,index=False)
    except Exception as err:
        msgbox.showinfo("错误",
        "保存文件%s时出错，可能是您未关闭这个文件。(%s:%s)"%(filename,type(err).__name__,str(err)))

FILETYPES=[("Excel xlsx文件","*.xlsx"),("CSV文件","*.csv"),
            ("pickle文件(*.pkl)","*.pkl"),("所有文件","*.*")]
def open_file(event=None):
    if event is not None:master = scr._canvas.master # 如果用户通过按下快捷键保存
    else:master = win
    filename=filediag.askopenfilename(master=master,title='打开',filetypes=FILETYPES)
    if not filename:return
    load_file(filename)
def save_file(event=None):
    if event is not None:master = scr._canvas.master # 如果用户通过按下快捷键保存
    else:master = win
    filename=filediag.asksaveasfilename(master=master,title='保存',
                            filetypes=FILETYPES,defaultextension='.xlsx')
    if not filename:return
    save(filename)
def switch_tip_mode(event=None):
    # 切换显示提示信息的模式
    gs.show_tip = (gs.show_tip+1)%3
def switch_acceleration(event=None):
    if gs.enable_accelerate:
        gs.speed=6
        gs.dt *= 0.004/0.00006
    else:
        gs.speed=340
        gs.dt *= 0.00006/0.004
        gs.enable_collision=False
    gs.enable_accelerate = not gs.enable_accelerate
def switch_collision(event=None):
    if not gs.enable_accelerate:
        gs.enable_collision = not gs.enable_collision
    else:gs.enable_collision = False
def switch_label(event=None):
    gs.show_label = not gs.show_label

def show_help():
    msgbox.showinfo("帮助",__doc__,master=win)
def exit():
    win.destroy();scr.bye() # 关闭窗口

def main():
    global scr,gs,win
    scr=Screen()
    scr.screensize(6000,6000)
    try:
        scr._canvas.master.state("zoomed")
    except TclError:pass
    scr.bgcolor("black")
    scr.tracer(0,0)

    win=tk.Tk()
    win.title("控制")
    win.geometry("210x85")
    win.protocol("WM_DELETE_WINDOW",lambda:win.iconify()) # 关闭控制窗口时自动最小化
    btns=tk.Frame(win)
    btns.pack(side=tk.TOP)

    file = "默认天体列表.xlsx"
    if len(sys.argv)>1:
        file=sys.argv[1]
    gs = GravSys()
    if os.path.isfile(file):
        load_file(file)
    else:
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

    # 绑定事件
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
    cv.bind_all("<Control-Key-o>",open_file) # 打开和保存快捷键
    cv.bind_all("<Control-Key-s>",save_file)
    cv.bind_all("<F3>",switch_tip_mode)
    cv.bind_all("<F4>",switch_label)
    cv.bind_all("<F5>",switch_acceleration)
    cv.bind_all("<F6>",switch_collision)
    cv.bind("<Button-1>",gs._onclick)
    cv.bind("<B1-Motion>",gs._ondrag)
    cv.bind("<B1-ButtonRelease>",gs._onrelease)
    ttk.Button(btns,text="加速",command=gs.increase_speed,width=5).grid(row=0,column=0)
    ttk.Button(btns,text="减速",command=gs.decrease_speed,width=5).grid(row=0,column=1)
    ttk.Button(btns,text="隐藏/显示轨道",command=gs.switchpen,width=15).grid(row=0,column=2,columnspan=2)
    ttk.Button(btns,text="放大",command=lambda:gs.zoom(4/3),width=5).grid(row=1,column=0)
    ttk.Button(btns,text="缩小",command=lambda:gs.zoom(3/4),width=5).grid(row=1,column=1)
    ttk.Button(btns,text="切换天体",command=gs.switch,width=13).grid(row=1,column=2,columnspan=2)
    ttk.Button(btns,text="打开",command=open_file,width=5).grid(row=2,column=0)
    ttk.Button(btns,text="保存",command=save_file,width=5).grid(row=2,column=1)
    ttk.Button(btns,text="帮助",command=show_help,width=5).grid(row=2,column=2)
    ttk.Button(btns,text="退出",command=exit,width=5).grid(row=2,column=3)
    cv.focus_force()

    globals().update(locals()) # 便于程序退出后, 在交互模式(>>> )中调试程序
    gs.init()
    try:gs.start()
    except (Terminator,tk.TclError):
        try:win.destroy()
        except tk.TclError:pass

if __name__ == '__main__':main()
