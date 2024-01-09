import time,sys,tkinter
from turtle import *

#定义常量
UP=90
DOWN=-90
LEFT=180
RIGHT=0
CLOCKWISE=[UP,RIGHT,DOWN,LEFT]
ANTICLOCKWISE=[UP,LEFT,DOWN,RIGHT]

def draw_square(size):
        for n in range(4):
            forward(size)
            right(90)

class Square(Turtle):
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
        hideturtle()#隐藏默认的海龟
    
class Grid(Square):
    def __init__(self,size=25,
                 direction=CLOCKWISE,
                 color="white",
                 fast=False):
        super().__init__(size,direction,color)
        self.direction=direction
        self.count=1.5
        self.fast=fast
        if fast:tracer(False)
        
    def draw(self):
        for direc in self.direction:
            self.setheading(direc)
            self.forward(self.size*int(self.count))
            self.stamp()#拷贝一份自身的形状,即绘制正方形
            self.count+=0.5
            if self.fast:
                update()
            
def main():
    shape("triangle")
    fillcolor("green")
    g=Grid(color="brown",fast=("--fast" in sys.argv))
    delay(0)
    while True:
        g.draw()

if __name__=="__main__":
    try:main()
    except (Terminator,tkinter.TclError):pass