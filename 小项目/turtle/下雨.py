import random,button,turtle
from turtle import *
from random import random
import os

def click(x,y):
    "鼠标单击事件"
    global buttons,scr,writer,raining #定义全局变量
    #判断用户单击的是哪个按钮
    if y<buttons[0].lly and y>buttons[0].ury:
        w=buttons[0].w
        if x>-120 and x<w-120:
            speed=5     #如果是小雨
        elif x>2*w-120 and x<3*w-120:
            speed=10 #如果是中雨
        elif x>4*w-120 and x<5*w-120:
            speed=20 #如果是大雨
        else:speed=None
        #擦除文字
        while writer.undobufferentries()>2:
            writer.undo()
        raining=False
        if speed:rain(speed)

def rain(speed=5):
    "下雨"
    global raining
    if not raining:#如果没有开始下雨
        app_path=os.path.split(os.path.realpath(__file__))[0]#获取程序路径
        scr.bgpic(app_path+"/图片/雨天.gif")#加载图片
        raining=True
        turtle.speed(0)
        tracer(False)
        
        def draw(x,y,undo=True):
            '画一个"雨点"'
            if undo:turtle.undo()
            goto(x,y)
            dot(5,"white")

        #声明两个新列表,用于记录水滴坐标
        delta=400//speed
        x=[0]*4
        y=[0]*4
        starty=[0]*4
        while True:
            #随机选择"水滴"开始流下的坐标
            for n in range(4):
                x[n]=random()*600-300
                y[n]=random()*250+100
                starty[n]=random()*400-400
                i=0
            while i<=delta:
                for n in range(4):
                    y[n]-=speed
                    draw(x[n],y[n],(not i==delta))
                update()
                i+=1

def main():
    global buttons,scr,writer
    hideturtle()#隐藏画笔
    delay(0)
    scr=getscreen()
    scr.setup(width=650, height=800)#设置画图窗口大小
    
    #绘制提示文本
    writer=Turtle()
    writer.penup()
    writer.hideturtle()
    writer.goto(-120,150)
    writer.write('单击按钮,选择"下雨"速度',font=("微软雅黑",20))
    #绘制三个按钮
    penup()
    buttons=[None]*3
    text=["小雨","中雨","大雨"]
    goto(-150,25)
    for n in range(3):
        buttons[n]=button.Button()
        buttons[n].w=70;buttons[n].h=40
        buttons[n].color1=[180]*3
        buttons[n].color2=[140]*3
        buttons[n].text=text[n]
        buttons[n].font="华文行楷"
        buttons[n].fontsize=20
        buttons[n].draw()
        left(107)
        forward(140)
        setheading(0)
    scr.onclick(click)
    scr.mainloop()

if __name__=="__main__":main()