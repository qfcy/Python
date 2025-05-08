"""快捷键:
按Ctrl+“+”或Ctrl+“-”进行缩放。
按↑，↓，←，→键移动。
按“+”或“-”键增加或者降低速度。
单击屏幕开启或关闭轨道显示。
单击行星即可跟随该行星。

另外，在程序目录下的表格中找到"天体列表.xlsx",
进入编辑, 即可自定义各种天体。
编辑过程中，点击Excel左下方的"帮助(必看)", 可查看表格的说明。
"""
from time import perf_counter
from random import randrange
import math,turtle,pickle,os,sys
from turtle import *
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as msgbox

import pandas as pd

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

scr=None

class GravSys:
    # 引力系统
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
    def start(self): # 主循环, 最关键的函数
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
画面速度: %.2f
""" % (self.fps, self.scale, self.dt*10**3)
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
    def follow(self,planet):
        if self.following:
            self.following.onfollow(False)
        self.following=planet
        self.key_x=self.key_y=0
        planet.onfollow(True)
        scr.ontimer(self.clear_scr, int(1000/self.fps))
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

    def switchpen(self): # 隐藏/显示行星轨道
        for planet in self.planets:
            if not planet.has_orbit:
                continue
            if planet.isdown():
                planet.penup()
            else:planet.pendown()
            planet.clear()
    def onclick(self,event=None): # 用于处理鼠标单击
        x,y=event.x,event.y
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

    def clear_removed_planets(self): # 清除已移除天体留下的轨道
        for planet in self.removed_planets:
            planet.clear()
        self.removed_planets=[]
    def remove(self,planet): # 移除天体
        self.removed_planets.append(planet)
        self.planets.remove(planet)
        planet._size = 1e-323 # 接近0
        planet.hideturtle()
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
    def distance(self,other): # 获取两天体间距离
        return math.hypot(self.x-other.x,
                          self.y-other.y)
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
            b = G * self.m / math.hypot(dx,dy)**3
            planet.ax-=b * dx
            planet.ay-=b * dy
    def step(self):
        pass
    def update(self):
        self.setpos((self.x+self.gs.scr_x)*self.gs.scale,
                    (self.y+self.gs.scr_y)*self.gs.scale)
        if self.rotation is not None:
            self.left(self.rotation*self.gs.dt)

scr=Screen()
scr.screensize(6000,6000)
try:
    scr._canvas.master.state("zoomed")
except TclError:pass
scr.bgcolor("black")
scr.tracer(0,0)

# 创建tkinter 界面
def show_help():
    msgbox.showinfo("帮助",__doc__,master=win)
def exit():
    win.destroy();scr.bye() # 关闭窗口
win=tk.Tk()
win.title("控制")
win.geometry("210x85")
btns=tk.Frame(win)
btns.pack(side=tk.TOP)

gs = GravSys()

table = str.maketrans("（），“”【】",'(),""[]') # 用于将中文标点转换为英文标点
if os.path.isfile("天体列表.xlsx"):
    lst=pd.read_excel("天体列表.xlsx",dtype=str)

    for i in range(len(lst)):
        line = lst[i:i+1] # 取出一行数据,line为DataFrame类型
        kwargs={} # 初始化天体的参数
        # 取出初始化天体的各个参数
        for key in line:
            values = line[key] # values为Series类型
            if len(values) == 0:
                continue
            # values[i] 才是这个表格内容的数据
            if str(values[i])=="nan": # 空值
                continue
            value = values[i].translate(table) # 转英文标点
            try:kwargs[key] = eval(value)
            except NameError:kwargs[key]=value # 用于处理name列
            except Exception as err:
                # 显示错误信息
                msgbox.showinfo("","""读取表格第 %d 行 %s 列出错，请修改您的天体列表。
%s: %s""" % (i+1+1, key,type(err).__name__,str(err)))
        if kwargs == {}:
            continue # 忽略表格中的空行

        del kwargs["type"]
        type_ = eval(line["type"][i]) # 取出天体所属的类
        type_(gs,**kwargs) # 初始化天体实例

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
        ast=Star(gs,"小行星%d"%i, AST_MASS,(0,0),(0,0),
                      0.1,shape=("circle","gray"),has_orbit=False)
        ast.setheading(randrange(360))
        ast.forward(randrange(700,800))
        ast.x,ast.y=ast.pos()
        v = ast.pos().rotate(90)
        ast.dx,ast.dy=v[0]/7,v[1]/7

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
cv.bind_all("<Key-Tab>",gs.switch)
cv.bind_all("<Key-Delete>",gs.del_planet)
cv.bind_all("<Shift-Key-Tab>",gs.reverse_switch)
cv.bind_all("<Control-Key-equal>",lambda event:gs.zoom(4/3.0)) #Ctrl+"+"
cv.bind_all("<Control-Key-minus>",lambda event:gs.zoom(3/4.0)) #Ctrl+"-"
cv.bind_all("<Button-1>",gs.onclick)
ttk.Button(btns,text="加速",command=gs.increase_speed,width=5).grid(row=0,column=0)
ttk.Button(btns,text="减速",command=gs.decrease_speed,width=5).grid(row=0,column=1)
ttk.Button(btns,text="隐藏/显示轨道",command=gs.switchpen,width=15).grid(row=0,column=2,columnspan=3)
ttk.Button(btns,text="放大",command=lambda:gs.zoom(4/3),width=5).grid(row=1,column=0)
ttk.Button(btns,text="缩小",command=lambda:gs.zoom(3/4),width=5).grid(row=1,column=1)
ttk.Button(btns,text="切换行星",command=gs.switch,width=11).grid(row=1,column=2,columnspan=2)
ttk.Button(btns,text="查看帮助",command=show_help,width=11).grid(row=2,column=0,columnspan=2)
ttk.Button(btns,text="退出",command=exit,width=5).grid(row=2,column=2)
cv.focus_force()

gs.init()
try:gs.start()
except (Terminator,tk.TclError):
    try:win.destroy()
    except tk.TclError:pass