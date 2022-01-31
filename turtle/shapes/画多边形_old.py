import sys
from turtle import *
# 表示颜色值的字典
color_list={"红色":"red","橙色":"orange","黄色":"yellow","绿色":"green","蓝色":"blue","紫色":"purple","粉色":"purple","黑色":"black","白色":"white","褐色":"brown","棕色":"brown","灰色":"gray"}

def trans(color,fill):
    "设置turtle画笔,或填充颜色"
    if color!="":
        if color in color_list.keys():
            color=color_list[color]#获取字典中的颜色值
        else:
            try:
                color=color_list[color+"色"]
            except:pass#错误处理
        if fill==True:fillcolor(color)#判断是否设置填充颜色
        else:pencolor(color)#设置画笔颜色

def main():
    if len(sys.argv)>1:
        try:
            sys.stdin=open(sys.argv[1])
        except OSError as err:print(err,file=sys.stderr)
    title("多边形")#设置窗口标题
    shape("turtle")
    penup()
    back(100)
    getscreen().colormode(255)
    fillcolor(212,212,212) #设置"海龟"颜色
    
    scr=getscreen()
    while True:#使程序永远循环
        color=input("输入图形颜色(选填）:")
        if color:trans(color,fill=True)
        bian=int(input("输入边数:"))
        length=int(input("边长(单位:像素):"))
        x=1
        pendown() #开始画图
        begin_fill()
        while x<=bian:   #循环,直到画出所有的边
            forward(length)#画多边形
            right(360/bian)
            x+=1
        end_fill()
        penup()
        forward(length*bian/2.1)

if __name__=="__main__":main()
