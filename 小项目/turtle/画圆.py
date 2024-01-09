import turtle
import time
#画一个蓝色点
turtle.dot(6,"blue")
#设置画笔颜色为绿色
turtle.pencolor("green")
# 当前位置(0,0)开始逆时针画半径为30的圆
turtle.circle(30)
# 逆时针画半径为50的半圆
turtle.circle(50, 180)
# 方向值为180,“standard”模式时方向向左,“logo”模式方向向下
turtle.circle(-50, 180)
#暂停程序
time.sleep(0.2)
#设置画笔颜色为蓝色
turtle.pencolor("purple")
# 逆时针方向半径为40画五边形(5步画接近整圆的图形)
turtle.circle(40, None, 5)
#画一个红点
turtle.dot(6,"red")
#让程序暂停,不立即关闭
time.sleep(2)