"画出许多的房子,呈现一片村野景象。"

import turtle,time
from turtle import *

def draw(size):
    "画出一栋房子"
    colormode(255)
    fillcolor(239,220,215)
    begin_fill()
    pendown()
    draw_rectangle(size,size/1.95)#画出房子主体
    end_fill()
    fillcolor(255,100,100)
    begin_fill()
    left(45)
    forward(size*0.7)#画出屋顶
    right(90)
    forward(size*0.7)
    end_fill()
    
    penup()
    right(129)
    forward(size*0.81)
    draw_window(size/5)#画出窗户
    penup()
    forward(size/3.8)
    draw_window(size/5)
    penup()
    right(150)
    forward(size*0.5)
    pendown()
    fillcolor(186,90,90)
    begin_fill()
    draw_rectangle(size/7,size/6)#画出门
    end_fill()

def draw_window(size):
    "画出窗户"
    setheading(0)
    fillcolor("white")
    pendown()
    begin_fill()
    draw_rectangle(size,size)
    end_fill()
    forward(size/2)
    right(90)
    forward(size)
    penup()
    right(135)
    forward(size*0.7)
    pendown()
    right(135)
    forward(size)
    left(90)
    forward(size/2)
    right(90)

def draw_rectangle(length,width):
    "画出一个长方形"
    setheading(0)
    for n in range(2):
        forward(length)
        right(90)
        forward(width)
        right(90)

def draw_houses(size,n):
    """画出并排的房子
    size:单个房子的尺寸
    n:房子个数"""
    for i in range(n):
        draw(size)
        penup()
        left(19)
        forward(size)
        pendown()

def main():
    scr=getscreen()
    scr.screensize(canvwidth=620,canvheight=800)#设置画图窗口大小
    scr.delay(0)#将绘图速度设为最快
    penup()
    goto(-360,0)
    draw_houses(n=8,size=60)#画出8栋房子
    penup()
    setheading(185)
    forward(700)
    setheading(0)
    pendown()
    draw_houses(n=8,size=70)#画出8栋略大的房子
    shape("turtle")#设置"海龟"的形状
    scr.mainloop()#使程序不关闭

if __name__=="__main__":
    try:main()
    except Terminator:pass
