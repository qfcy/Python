from turtle import *
import 画多边形

title("多边形")#设置窗口标题
penup()
back(100)
shape("turtle")
colormode(255)
pencolor(120,120,120) #设置"海龟"颜色

scr=getscreen()
while True:#使程序永远循环
    color=scr.textinput("","输入图形颜色(选填）:")
    if color:画多边形.trans(color,True)
    a=scr.numinput("","角的个数(必须为奇数):")
    length=scr.numinput("","尺寸(单位:像素):")
    pendown() #开始画图
    begin_fill()
    for n in range(a):
        forward(length)
        right(180-180/a)
    end_fill()
    penup()
    forward(length*1.3)
