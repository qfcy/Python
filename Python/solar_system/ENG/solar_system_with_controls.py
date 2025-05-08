# -*- coding: utf-8 -*-
"""
Solar System Simulation using tkinter with control buttons.

Shortcut keys:
Press Ctrl+"+" or Ctrl+"-" to zoom.
Press ↑, ↓, ←, → to move.
Press "+" or "-" to increase or decrease speed.
Click on the screen to switch on or off the display of orbits.
Click on a planet to follow it.
Drag the mouse to launch spacecrafts.

Version 1.2.6 update: Added control the spacecraft by pressing the direction keys after following the ship.
Version 1.3.1: Added shortcut keys Tab and Shift+Tab to switch between celestial bodies.
Version 1.3.2: Added the feature of deleting celestial bodies and saving data using module pickle.
Version 1.3.3: Fixed bugs in saving celestial data and optimized the source code.
Added shortcut key Ctrl+D to delete all ships.
"""
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
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as msgbox
import tkinter.filedialog as filediag

import pandas as pd

__version__="1.3.3"

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

class GravSys(solar_system.GravSys):
    # 引力系统
    __slots__=solar_system.GravSys.__slots__+["calc_time"]
    def __init__(self,scr=None):
        self.scr = scr or Screen()
        self.planets = []
        self.removed_planets=[]
        self.G = 8
        self.t = 0
        self.dt = 0.004 # 时间速度，每次计算经过的时间
        #speed: 画面速度，程序在绘制一帧之前执行计算的次数
        self.speed=6
        self.scale=1 # 缩放比例
        self.scr_x=self.key_x=0 # scr_x,scr_y:视野的偏移距离
        self.scr_y=self.key_y=0
        self.show_tip=1;self.fps=20
        self.calc_time=0
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
            calc_starttime=perf_counter()
            # 计算行星的位置
            for _ in range(self.speed):
                self.t += self.dt
                for p in self.planets: # 计算各行星加速度
                    p.acc()
                for p in self.planets: # 计算速度、位移
                    p.step()
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
                    left_border=255
                else:
                    tip = self.detailed_info()
                    left_border=465
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
        tip = "fps:%d\nScale: %.4f\nSpeed: %.4f\n" % (
                        self.fps, self.scale, self.dt)
        if self.following:
            follow = self.following
            tip += "\nFollowing: %s\nMass: %d" % (follow.name,follow.m)
            if getattr(follow,'parent',None):
                tip+="\nDistance to %s: %d" % (follow.parent.name,
                        follow.distance(follow.parent))
            if isinstance(follow,SpaceCraft):
                if getattr(follow,'parent',None):
                    # 计算飞船相对父天体速度
                    dx,dy = follow.dx-follow.parent.dx, \
                            follow.dy-follow.parent.dy
                else:dx,dy = follow.dx, follow.dy
                tip+="\nSpacecraft speed: %.6f" % math.hypot(dx,dy) # hypot相当于math.sqrt(dx**2+dy**2)
                tip+="\nPress ↑,↓,←,→ to control\nthe spacecraft."
            tip += "\n\nPress F3 to view the detailed\ninformation."
        return tip
    def detailed_info(self):
        tip = "fps:{:.0f}\nZoom scale: {:.10g}\n".format(self.fps, self.scale)
        tip += "Time: {:#.12g}\tSpeed: {:#.4f}\n".format(self.t, self.dt)
        if self.following:
            follow = self.following
            tip += "\nFollowing: {}\nMass: {:.10g}".format(follow.name,follow.m)
            if getattr(follow,'parent',None):
                tip+="\nDistance to {}: {}".format(follow.parent.name,
                        follow.distance(follow.parent))
                center = (follow.parent.x,follow.parent.y)
                # 计算天体相对父天体速度
                dx,dy = follow.dx-follow.parent.dx, \
                        follow.dy-follow.parent.dy
            else:
                center = (0,0)
                dx,dy = follow.dx, follow.dy

            x, y = follow.x, follow.y
            tip+="\nPosition: ({:.16g}, {:.16g})".format(x,y)
            tip+="\nRelative Velocity: ({:.10g}, {:.10g})".format(dx,dy)
            tip+="\n\t    ({:.16g})\tAngle: {:.4f}°".format(
                math.hypot(dx,dy), math.atan2(dy,dx)/math.pi*180)
            tip+="\nResultant gravity force: {:.10g}".format(follow.calc_acc()*follow.m)
            if follow.parent:
                ecc, semimajor_axis, angle_peri=follow.calc_orbit()
                tip+="\nEccentricity: {:.5g}\tSemimajor axis: {:.8g}".format(ecc,semimajor_axis)
                tip+="\nPeriapsis angle: {:.4f}°".format(angle_peri)

            dx_s, dy_s = dx*self.dt, dy*self.dt
            next_x, next_y = x+dx_s, y+dy_s
            tip+="\n"
            tip+="\nMovement per tick：({:.8g}, {:.8g})".format(dx_s,dy_s)
            # 天体相对父天体公转的角度
            tip+="\nOrbital angle per tick：{:.8g}°".format(calc_angle(center,(x,y),(next_x,next_y)))
            if not (x==0 or y==0):
                prec_x=get_floating_point_precision(x)
                prec_y=get_floating_point_precision(y)
                # 倍数为单次计算位移与浮点数精度之比
                tip+="\nFloating-point precision loss：x:2^{}({:.4g} times),\n\t\ty:2^{}({:.4g} times)".format(
                    prec_x, abs(dx_s)/2**prec_x, prec_y, abs(dy_s)/2**prec_y)

            # 程序运行中需要计算和渲染，这是单次循环中计算时间占总运行时间的比例
            tip+="\n\nPropotion of calculation time：{:.4g}%".format(self.calc_time/(1/self.fps)*100)
            tip+="\n\nNote:Press the scrollbar to hold the movement\n     temporarily and view the data."
        return tip
    _onrelease=_copy_func(solar_system.GravSys._onrelease,globals()) # 使用本模块中的SpaceCraft类

class Star(solar_system.Star):
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

class RoundStar(solar_system.RoundStar,Star):
    pass

class Sun(solar_system.Sun,Star):
    pass

class SpaceCraft(solar_system.SpaceCraft,Star):
    pass

# 避免eval()函数产生安全漏洞
globals_ = globals()
def _safe_eval(expr):
    if expr in globals_:
        value = globals_[expr] # 从全局变量中直接取出
        if issubclass(value,Star): # 仅允许Star的子类
            return value
        else:
            return None
    else:
        dct = {"__builtins__":{}, # 不允许调用内置函数
                "TRUE":True,"FALSE":False} # 允许使用Excel中"TRUE"和"FALSE"的数据
        return _old_eval(expr,dct)
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
    table = str.maketrans("（），。“”【】",'(),.""[]') # 用于将用户输入的全角标点转换为半角标点
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
        msgbox.showinfo("Error","Error reading file %s.(%s:%s)"%(filename,type(err).__name__,str(err)))
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
                    msgbox.showinfo("Error","No parent object found for celestial body %s."%kwargs["name"])
                    del kwargs["parent"]
                else:
                    kwargs["parent"]=parent
            if "sun" in kwargs:
                sun=find_planet(gs,kwargs["sun"])
                if sun is None:
                    msgbox.showinfo("Error","No parent star found for celestial body %s."%kwargs["name"])
                    del kwargs["sun"]
                else:
                    kwargs["sun"]=sun
            star_type(gs,**kwargs) # 初始化天体实例
        except Exception as err:
                # 显示错误信息
                msgbox.showinfo("Error",
                'Error reading row %d column "%s" ,Please check the file %s.\n%s: %s' % (
                    i+1+1, key, filename, type(err).__name__,str(err)))
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
            attr_list=["t","dt","speed","scale","G","show_tip","show_orbit"]
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
        msgbox.showinfo("Error",
        "An error occurred while saving file %s.(%s:%s)"%(filename,type(err).__name__,str(err)))

FILETYPES=[("Excel xlsx","*.xlsx"),("CSV File","*.csv"),
            ("Python pickle file(*.pkl)","*.pkl"),("All Files","*.*")]
def open_file(event=None):
    if event is not None:master = scr._canvas.master # 如果用户通过按下快捷键保存
    else:master = win
    filename=filediag.askopenfilename(master=master,title='Open',filetypes=FILETYPES)
    if not filename:return
    load_file(filename)
def save_file(event=None):
    if event is not None:master = scr._canvas.master # 如果用户通过按下快捷键保存
    else:master = win
    filename=filediag.asksaveasfilename(master=master,title='Save',
                            filetypes=FILETYPES,defaultextension='.xlsx')
    if not filename:return
    save(filename)
def switch_tip_mode(event=None):
    # 切换显示提示信息的模式
    gs.show_tip = (gs.show_tip+1)%3
def show_help():
    msgbox.showinfo("Help",
                    "For help, please refer to file README.md.",master=win)
def exit():
    win.destroy();scr.bye() # 关闭窗口

scr=None
def main():
    global scr,gs,win
    scr=Screen()
    scr.title("Python gravity simulator")
    scr.screensize(6000,6000)
    try:
        scr._canvas.master.state("zoomed")
    except TclError:pass
    scr.bgcolor("black")
    scr.tracer(0,0)

    win=tk.Tk()
    win.title("Control")
    win.geometry("260x85")
    win.protocol("WM_DELETE_WINDOW",lambda:win.iconify()) # 关闭控制窗口时自动最小化
    btns=tk.Frame(win)
    btns.pack(side=tk.TOP)

    file = "default.xlsx"
    if len(sys.argv)>1:
        file=sys.argv[1]
    gs = GravSys()
    if os.path.isfile(file):
        load_file(file)
    else:
        sun = Sun(gs,"Sun",SUN_MASS, (0,0), (0,0),
                  2.3,has_orbit=False,shape=('yellow',))
        mercury = Star(gs,"Mercury",MERCURY_MASS, (60,0), (0,330),
                       0.5, shape=("#b3b3b3","#7f7f7f","#4d4d4d"))

        venus = Star(gs,"Venus",VENUS_MASS, (-130,0), (0,-250),
                     0.7, shape=("gold","brown","gold4"))

        earth = Star(gs,"Earth",EARTH_MASS, (260,0), (0,173),
                     0.8, shape=("blue","#00008b","blue"))

        moon = Star(gs,"Moon",MOON_MASS, (269,0), (0,262),
                    0.5,shape=("#b3b3b3","#4d4d4d","gray30"),
                    has_orbit=False, parent=earth)

        mars = Star(gs,"Mars",MARS_MASS, (0,430), (-140, 0),
                    0.6, shape=("red","#8b0000","red"))
        phobos = Star(gs,"Phobos",PHOBOS_MASS, (0,438), (-167, 0),
                      0.1,shape=('circle',"orange"),
                      has_orbit=False,parent=mars)
        phobos.fillcolor("orange")

        # 创建小行星
        for i in range(10):
            ast=RoundStar(gs,"Asteroid%d"%i, AST_MASS,(0,0),(0,0),
                          0.05,has_orbit=False)
            ast.setheading(randrange(360))
            ast.forward(randrange(700,800))
            ast.x,ast.y=ast.pos()
            v = ast.pos().rotate(90)
            ast.dx,ast.dy=v[0]/7,v[1]/7
            ast.pu()
            ast.color("gray")

        # 木星及卫星
        jupiter = Star(gs, "Jupiter", JUPITER_MASS, (1100,0), (0, 86),
                       1.2,shape=("#ffd39b","#8b7355","#8b6508"))
        Io = Star(gs,"Io", MOON_MASS, (1125,0), (0,145),
                   0.05, shape=("circle","yellow"),
                   has_orbit=False,parent=jupiter)
        europa = Star(gs,"Europa", MOON_MASS, (1142,0), (0,134),
                   0.07,shape=("circle","#cd950c"),
                   has_orbit=False,parent=jupiter)
        # 土星
        saturn = Star(gs,"Saturn",SATURN_MASS, (2200,0), (0, 60),
                      1.0, shape=("#fff68f","#8b864e","#8b864e"))
        # 天王星
        uranus = Star(gs, "Uranus", URANUS_MASS, (0, 4300), (-43, 0),
                      0.8, shape=("#add8e6","blue","blue"))
        # 海王星
        neptune = Star(gs, "Neptune", NEPTUNE_MASS, (7500,0), (0, 34),
                       0.8, shape=("blue","#483d8b","#191970"))
        nereid = Star(gs, "Nereid", MOON_MASS, (7600,0), (0, 48),
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
    cv.bind("<Button-1>",gs._onclick)
    cv.bind("<B1-Motion>",gs._ondrag)
    cv.bind("<B1-ButtonRelease>",gs._onrelease)
    ttk.Button(btns,text="Fast",command=gs.increase_speed,width=8).grid(row=0,column=0)
    ttk.Button(btns,text="Slow",command=gs.decrease_speed,width=8).grid(row=0,column=1)
    ttk.Button(btns,text="Hide/Show orbits",command=gs.switchpen,width=18).grid(row=0,column=2,columnspan=3)
    ttk.Button(btns,text="Zoom in",command=lambda:gs.zoom(4/3),width=8).grid(row=1,column=0)
    ttk.Button(btns,text="Zoom out",command=lambda:gs.zoom(3/4),width=8).grid(row=1,column=1)
    ttk.Button(btns,text="Switch planets",command=gs.switch,width=18).grid(row=1,column=2,columnspan=2)
    ttk.Button(btns,text="Open",command=open_file,width=8).grid(row=2,column=0)
    ttk.Button(btns,text="Save",command=save_file,width=8).grid(row=2,column=1)
    ttk.Button(btns,text="Help",command=show_help,width=8).grid(row=2,column=2)
    ttk.Button(btns,text="Exit",command=exit,width=8).grid(row=2,column=3)
    cv.focus_force()

    globals().update(locals()) # 便于程序退出后, 在交互模式(>>> )中调试程序
    gs.init()
    try:gs.start()
    except (Terminator,tk.TclError):
        try:win.destroy()
        except tk.TclError:pass

if __name__ == '__main__':main()
