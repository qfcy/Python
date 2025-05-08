from turtle import *
from tkinter import TclError

#定义常量
UP=90
DOWN=-90
LEFT=180
RIGHT=0
CLOCKWISE=[UP,RIGHT,DOWN,LEFT]
ANTICLOCKWISE=[UP,LEFT,DOWN,RIGHT]

def draw_square(size):
    "画一个尺寸为size的正方形"
    for n in range(4):
        forward(size)
        right(90)

class Square(Turtle):
    "一个正方形形状的Turtle"
    def __init__(self,size=25,
                 direction=RIGHT,
                 color="white"):
        super().__init__()
        self.size=size
        self.direction=direction
        self.fillcolor(color)
        
        begin_poly()# 开始记录正方形形状
        draw_square(self.size)
        end_poly()# 结束记录
        poly=get_poly()
        register_shape("square", poly)
        self.shape("square")#将自身的形状设置为记录的形状

    
class Grid(Square):
    """"一个网格的类
    参数:size:网格中一个正方形的尺寸
    direction:绘制方向
    color:网格颜色"""
    def __init__(self,size=25,
                 direction=CLOCKWISE,
                 color="white",
                 fast=False):
        super().__init__(size,direction,color)
        self.direction=direction
        self.count=1.5
        self.__fast=fast
        if fast:tracer(False)
    def draw(self):
        while True:
            for direc in CLOCKWISE:
                self.setheading(direc)
                self.draw_square(int(self.count))
                self.count+=0.5
                if self.__fast:update()
    def draw_square(self,count):
        "拷贝一份自身的形状,即绘制正方形"
        for n in range(count):
            self.forward(self.size)
            self.stamp()
def main():
    hideturtle()#隐藏默认的海龟
    tracer(4,0)
    delay(0)
    g=Grid(fast=True)
    g.draw()

if __name__=="__main__":
    try:main()
    except (Terminator,TclError):pass