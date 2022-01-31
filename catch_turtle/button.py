"""使用turtle模块绘制按钮的模块。
七分诚意制作   2019.4.24"""
import math,random
from turtle import *
class Button():
    "turtle绘制出的按钮类"
    def __init__(self,width=120,height=40):
        #定义类属性
        self.h=height
        self.w=width
        self.color1=self.color2=[0]*3
        self.font=self.text=""
        self.fontsize=12
        self.llx=self.lly=0#llx、lly:画布左上角x、y坐标
        self.urx=self.ury=0#urx、ury:画布右下角x、y坐标
    def draw(self):
        colormode(255)
        fillcolor(self.color1[0],self.color1[1],self.color1[2])
        begin_fill()
        self.llx=pos()[0]#记录画笔坐标
        self.lly=pos()[1]
        pencolor("black")
        
        pendown()#画出按钮上半部分
        forward(self.w)
        right(90)
        forward(self.h/2)
        right(90)
        penup()
        forward(self.w)
        right(90)
        pendown()
        forward(self.h/2)
        end_fill()
        
        fillcolor(self.color2[0],self.color2[1],self.color2[2])
        right(180) #画出按钮下半部分
        forward(self.h/2)
        begin_fill()
        forward(self.h/2)
        left(90)
        forward(self.w)
        self.urx=pos()[0]#再次记录画笔坐标
        self.ury=pos()[1]
        left(90)
        forward(self.h/2)
        end_fill()
        
        if self.text:#绘制文本
            penup()
            left(90)
            l=len(self.text)
            forward(self.w/2 + l*self.fontsize/1.5)
            left(90)
            forward(self.fontsize/2)
            write(self.text,True,align="left",font=(self.font,self.fontsize))
        goto(self.llx,self.ury)
    def inarea(self,x,y):
        "判断x,y这个坐标是否位于按钮内。"
        return x>self.llx and x<self.urx and y<self.lly and y>self.ury

def click(x, y):
    global a,b
    #判断用户单击的是哪个按钮
    if a.inarea(x,y):#如果是关于按钮
        try:
            showturtle()#显示画笔
            shape("triangle")#设置画笔形状为三角形
            delay(20)
            right(135)
            forward(320)
            for s in __doc__:
                write(s,True,align="left",font=("微软雅黑",20))#绘制文字
            hideturtle()#再次隐藏画笔
        except Terminator:pass
    if b.inarea(x,y):#如果是退出按钮
        print("bye!")
        bye()

def main():
    global a,b
    #初始化
    delay(0)
    penup()
    setx(-10)
    hideturtle()#隐藏画笔

    #绘制关于按钮
    a=Button()
    a.w=100;a.h=50
    a.color1=[0,180,0]
    a.color2=[0,140,0]
    a.text="关于"
    a.font="华文行楷"
    a.fontsize=20
    a.draw()
    
    forward(40)
    left(90)
    
    #绘制退出按钮
    b=Button()
    b.w=100;b.h=50
    b.color1=[0,180,0]
    b.color2=[0,140,0]
    b.text="退出"
    b.font="华文行楷"
    b.fontsize=20
    b.draw()
    
    scr=getscreen()
    scr.onclick(click)
    scr.mainloop()

if __name__=="__main__":main()