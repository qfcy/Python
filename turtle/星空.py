# 使用turtle模块画出星空
from random import randint,choice
from tkinter import TclError
from turtle import *
from turtle import Terminator
from time import sleep, perf_counter

__email__="3416445406@qq.com"
__author__="七分诚意 qq:3076711200 邮箱:%s"%__email__
__version__="1.0.3"

class Star(Turtle):
    def __init__(self):
        super().__init__()
        self.setundobuffer(None)
        self.setheading(randint(0,360))
        self.dt=randint(4,12)
        self.penup()
        self.shape("circle")
        self.shapesize(0.1)
        self.forward(self.dt*15)
        

        self._color=100
        self.color((self._color,)*3)
        self.removed=False
    def move(self):
        # 移动星星
        self.forward(self.dt)
        self.dt*=1.03
        # 使星的颜色变亮
        self._color=min(self._color+4,255)
        self.color((self._color,)*3)
        self.shapesize(self.shapesize()[0]*1.01)

def main():
    num=20 # 星星个数
    scr=Screen()
    win=scr._canvas.master
    # 使窗口全屏, 并隐藏画布_canvas的边框
    win.overrideredirect(True)
    #win.attributes("-fullscreen",True)
    x,y,w,h = 0,0, win.winfo_screenwidth(),win.winfo_screenheight()
    bd = scr._canvas["borderwidth"] or 4
    x-=bd;y-=bd;w+=bd*2;h+=bd*2
    win.geometry('%dx%d+%d+%d'% (w,h,x,y))
    onscreenclick(lambda x,y:win.destroy()) # 单击屏幕退出

    colormode(255)
    bgcolor("black")
    tracer(False)
    stars=[]
    for i in range(num):
        stars.append(Star())

    while True:
        start=perf_counter()
        for star in stars:
            star.move()
            # 移除屏幕外的星
            if abs(star.xcor())>window_width()/2 \
               or abs(star.ycor())>window_height()/2:
                star.hideturtle()
                stars.remove(star)
                star.removed=True
                
        update()

        for star in scr._turtles:
            if star.removed:
                scr._turtles.remove(star)

        sleep(max(0.05-(perf_counter()-start),0))
        if len(stars)<num:
            for i in range(num-len(stars)):
                stars.append(Star())

if __name__=="__main__":
    try:main()
    except (TclError,Terminator):pass
