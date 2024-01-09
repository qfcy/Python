import turtle
from turtle import *
import random
from random import random
import os

def draw(x,y):
    '画一个"雨点"'
    goto(x,y)
    dot(5,"white")

def _undo(times):
    for i in range(times):
        if undobufferentries():
            undo()

scr=Screen()
title("洞中流水")#设置窗口标题
turtle.setup(width=700, height=800)#设置画图窗口大小
scr.bgcolor("black")#设置背景颜色
app_path=os.path.split(__file__)[0]#获取程序路径
scr.bgpic(app_path+"/图片/岩壁.gif")#加载图片
penup()
hideturtle()#隐藏画笔

#声明两个新列表,用于记录水滴坐标
x=[0]*4
y=[0]*4
while True:
    #随机选择"水滴"开始流下的坐标
    speed(0)
    for n in range(4):
        x[n]=random()*600-300
        y[n]=random()*250+100
        i=0
    while i<30:
        for n in range(4):
            y[n]-=11
            draw(x[n],y[n])
        i+=1
    tracer(30,0)
    _undo(3)#撤销
    penup()
    tracer(1,1)
