from turtle import *

def move(x, y):
    # 海龟箭头移动到当前拖动位置
    global n
    goto(x,y)
    n+=1
    print("拖动次数:",n,"  x:",x,"y:",y)

def release(x,y):
    pendown()
    print('鼠标释放  位置',"  x:",x,"y:",y)

#绘制文本
delay(0)
penup()
goto(-40,150)
write("DRAG!",font=("黑体",30))
home()#移动到0,0位置
shape("turtle")
onrelease(release)
ondrag(move,btn=1)
n=1 #n:拖动次数

mainloop()#使程序不立即关闭