"游戏追逐海龟中的一些基本函数"
import random,time
from turtle import *

def drag(x,y):
    # 海龟箭头移动到当前拖动位置
    a.goto(x,y)

def moveturtles(a,b,catch=True):
    "使两个海龟爬动,并旋转,同时判断它们是否碰撞。"
    if mov:
        move(a,15)
    if mov:
        move(b)
    if mov and catch:
        l=25
        xcatch=a.xcor()-b.xcor()>-l and a.xcor()-b.xcor()<l
        ycatch=a.ycor()-b.ycor()>-l and a.ycor()-b.ycor()<l
        if catches(a,b) and mov:#判断海龟是否碰撞
            a.write("CATCH!",True,align="right",font=("黑体",14))#绘制文本
            a.clone()#复制海龟箭头
            b.clone()
            time.sleep(1.2)

def move(t,length=9,go=True):
    "使海龟爬动,并旋转"
    t.left(random.randrange(-300,300))
    if go:t.forward(length)
def catches(a,b,l=25):
    "判断海龟是否碰撞"
    xcatch=a.xcor()-b.xcor()>-l and a.xcor()-b.xcor()<l
    ycatch=a.ycor()-b.ycor()>-l and a.ycor()-b.ycor()<l
    return xcatch and ycatch

def stop():
    "停止海龟移动"
    global mov
    mov=False
def _continue():
    "继续海龟移动"
    global mov
    mov=True
def __onclick(x=0,y=0):
    if mov:stop()
    else:
        _continue()
        __move(a,b)

def bind(scr,t,length):
    """使某个海龟(t)绑定键盘事件。绑定后,
    按↑,↓,←,→键即可移动它,每次移动距离为length。"""
    def u():
        t.setheading(90)
        t.forward(length)
    def d():
        t.setheading(-90)
        t.forward(length)
    def l():
        t.setheading(180)
        t.forward(length)
    def r():
        t.setheading(0)
        t.forward(length)
    scr.onkey(u,"Up")
    scr.onkey(d,"Down")
    scr.onkey(l,"Left")
    scr.onkey(r,"Right")
    scr.listen()

def _undo(mintimes=0,x=0,y=0):
    "撤销,直到撤销次数>= mintimes"
    while undobufferentries()>mintimes:
        undo()
        delay(0)

def reset():
    "切换界面时清屏"
    clear()
    home()


def __move(a,b):
    while mov:
        moveturtles(a,b)#一直移动海龟
def main():
    #初始化两个turtle实例
    global a,b
    delay(0)
    scr=Screen()
    a=Turtle()
    b=Turtle()
    a.penup()
    b.penup()
    a.shape("turtle")
    b.shape("turtle")
    a.fillcolor("green")
    b.fillcolor("yellow")
    a.ondrag(drag)
    scr.onclick(__onclick)
    
    bind(scr,a,10)
    delay(5)
    __move(a,b)
    scr.mainloop()

mov=True
if __name__=="__main__":main()