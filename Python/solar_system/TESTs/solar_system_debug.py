# -*- coding: utf-8 -*-
# solar_system程序的调试，输出计算精度和性能等信息

# 程序中的计算精度由两个因素影响：单次计算的时间间隔(dt)、浮点数精度误差。

# 一方面，由于程序将天体运动分解成许多的小段，
# 如果单次计算的时间间隔过大(未远小于轨道周期)，会使单次计算中
# 天体相对父天体公转的角度增大，天体轨道不再精确，导致精度下降。
# (注意程序中的时间是虚拟时间，非现实时间。)
# 这一误差可通过减小dt来解决。但要使动画速度不变，dt越小，对计算速度的要求越高，
# 就需要性能更高的代码(参见solar_system_accelerate.py)

# 另一方面，Python默认使用双精度浮点数。
# 由于双精度浮点数仅有52位二进制的有效数字，天体的x、y坐标越大，浮点数精度误差越高，
# 而由于单次计算中天体在x,y轴只能移动最小精度的倍数，坐标过高时天体移动的计算不再精确。
# dt为0.0004时，若天体坐标小于或接近10^10~10^11，精度误差几乎可忽略。
# 坐标超过10^11之后，“距离现象”会逐渐变得明显。这一误差目前尚无解决办法。
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

            calc_time=perf_counter()-calc_starttime

            if self.following!=None:
                self.scr_x=-self.following.x+self.key_x
                self.scr_y=-self.following.y+self.key_y
            else:
                self.scr_x=self.key_x
                self.scr_y=self.key_y
            # 刷新行星
            for p in self.planets:
                p.update()

            self.fps=1/(perf_counter()-self.__last_time) # 计算帧率
            self.__last_time=perf_counter()

            # 显示文字及调试信息
            if self.show_tip:
                tip = "fps:{:.0f}\n放大倍数: {:.10g}\n".format(self.fps, self.scale)
                tip += "时间: {:#.12g}\t时间速度: {:#.4f}\n".format(self.t, self.dt)
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
                    tip+="\n单次计算(相对)位移：({:.8g}, {:.8g})".format(dx_s,dy_s)
                    # 天体相对父天体公转的角度
                    tip+="\n单次计算角度误差：{:.8g}°".format(calc_angle(center,(x,y),(next_x,next_y)))
                    if not (x==0 or y==0):
                        prec_x=get_floating_point_precision(x)
                        prec_y=get_floating_point_precision(y)
                        # 倍数为单次计算位移与浮点数精度之比
                        tip+="\n浮点数精度误差：x:2^{}({:.4g}倍),\n\t\ty:2^{}({:.4g}倍)".format(
                            prec_x, abs(dx_s)/2**prec_x, prec_y, abs(dy_s)/2**prec_y)

                    # 程序运行中需要计算和渲染，这是单次循环中计算时间占总运行时间的比例
                    tip+="\n\n计算时间占运行时间比例：{:.4g}%".format(calc_time/(1/self.fps)*100)
                    tip+="\n\n提示:可按住下方滚动条暂停模拟，更好地查看数据。"
                top_h=26;fontsize=12
                h = (tip.count("\n")+1)*(fontsize*3-4)/2 + top_h # 3和4为调试中推出的数值
                self.writer.clear()
                self.writer.goto(
                    scr.window_width()//2-405,scr.window_height()//2-h
                )
                self.writer.write(
                    tip,
                    font = (None,fontsize)
                )
            update()
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
    def getOrbitSpeed(self,r=None,other=None):
        # 获取某一半径的圆轨道上天体的速率
        # 引力=向心力=m * v**2 / r
        other=other or self.sun
        r=r or self.distance(other)
        return math.sqrt(self.grav(other,r) * r / self.m)

class RoundStar(solar_system.RoundStar,Star):
    pass

class Sun(solar_system.Sun,Star):
    pass

class SpaceCraft(solar_system.SpaceCraft,Star):
    pass

FLAG_SAVEFILE = False # 退出时是否自动保存数据到game.pkl
main=_copy_func(solar_system.main,globals())

if __name__ == '__main__':
    main()
