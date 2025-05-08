# -*- coding: utf-8 -*-
# 行星碰撞，及太阳系早期行星形成的简单模拟
# 碰撞算法原理：https://blog.csdn.net/qfcy_/article/details/119711166
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

SUN_MASS=1000000
AST_MASS=14000 # 修改

class GravSys(solar_system.GravSys):
    # 引力系统
    def __init__(self,scr=None):
        super().__init__(scr)
        self.dt = 0.0008 # 速度
        #speed: 程序在绘制一帧之前执行计算的次数
        self.speed=15
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
                    p.check_collision()
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
    def increase_speed(self,event=None):
        self.dt+=0.0001
    def decrease_speed(self,event=None):
        self.dt-=0.0001
    _onrelease=_copy_func(solar_system.GravSys._onrelease,globals()) # 使用本模块中的SpaceCraft类

class Star(solar_system.Star):
    def check_collision(self):
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
                rate = 0.2 # 碰撞的"弹性", 0为完全非弹性碰撞, 1为弹性碰撞
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
    def getOrbitSpeed(self,r=None,other=None):
        # 获取某一半径的圆轨道上天体的速率
        # 引力=向心力=m * v**2 / r
        other=other or self.sun
        r=r or self.distance(other)
        return math.sqrt(self.grav(other,r) * r / self.m)

class RoundStar(solar_system.RoundStar,Star):
    pass

class Sun(solar_system.Sun,Star):
    def step(self):
        self.x=self.y=self.dx=self.dy=0
    def check_collision(self): # 防止太阳受碰撞时移动
        super().check_collision()
        self.step()

class SpaceCraft(solar_system.SpaceCraft,Star):
    pass

def main():
    scr=Screen()
    scr.screensize(6000,6000)
    try:
        scr._canvas.master.state("zoomed")
    except TclError:pass
    scr.bgcolor("black")
    scr.tracer(0,0)

    gs = GravSys(scr)
    sun = Sun(gs,"太阳",SUN_MASS, (0,0), (0,0),
              1.5,has_orbit=False,shape=('yellow',))

    # 创建小行星
    for i in range(12):
        ast=RoundStar(gs,"小行星%d"%i, AST_MASS,(0,0),(0,0),1)
        ast.setheading(randrange(360))
        ast.forward(randrange(50,150))#randrange(700,800))
        ast.x,ast.y=ast.pos()
        v = ast.getOrbitSpeed()
        vector = ast.pos().rotate(90) # 轨道方向为逆时针
        ast.dx,ast.dy = v*vector[0]/abs(vector), v*vector[1]/abs(vector)
        ast.color("green")
    for i in range(18):
        ast=RoundStar(gs,"小行星%d"%i, AST_MASS,(0,0),(0,0),1)
        ast.setheading(randrange(360))
        ast.forward(randrange(500,600))#randrange(700,800))
        ast.x,ast.y=ast.pos()
        v = ast.getOrbitSpeed()
        vector = ast.pos().rotate(90) # 轨道方向为逆时针
        ast.dx,ast.dy = v*vector[0]/abs(vector), v*vector[1]/abs(vector)
        ast.color("green")
#     a1=RoundStar(gs,"小行星1", AST_MASS,(160,140),(-150,150),1)
#     a2=RoundStar(gs,"小行星2", AST_MASS,(150,150),(-150,150),1)
#     a3=RoundStar(gs,"小行星3", AST_MASS,(170,130),(-150,150),1)

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
    gs.switchpen() # 隐藏轨道
    try:gs.start()
    except (Terminator,TclError):pass

if __name__ == '__main__':
    main()
