import turtle
from turtle import *
import 画多边形

scr=getscreen()
color=scr.textinput("输入颜色","输入图形颜色(选填）:")
if color:画多边形.trans(color,False)

shape("turtle")
penup()
back(100)
pendown()
while True:#使程序永远循环
    length=scr.numinput("","移动的距离(单位:像素):")
    angle=scr.numinput("","角度:")
    times=scr.numinput("","循环次数:")
    x=1
    dot(4,"red")#在起点画红色圆点
    while x<=times:   #循环,直到画出所有的边
        forward(length)
        right(angle)
        x+=1
    dot(2,"blue")#在终点画蓝色圆点