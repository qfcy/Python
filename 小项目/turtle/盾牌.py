# 导入 turtle 模块
# 模块是 python 自带的工具箱，这里将工具箱导入就能使用了
# turtle 模块是 python 用来画图的工具箱
import turtle
# 这一行用来控制绘图延迟
turtle.delay(0)
def draw():
    global t,l,scr#定义全局变量
    l=200
    # 创建一个Screen类，赋给scr变量
    scr=turtle.Screen()
    # 创建一个Turtle类，赋给t变量
    # 照猫画虎用就是了，这些东西要到很后面才能理解
    t = turtle.Turtle()
    # 这是向前走，单位是像素
    t.forward(100)
    # 这是转弯，单位是角度
    t.right(120)
    t.forward(100)
    t.right(120)
    t.forward(100)
    t.right(120)
    
    # 复制三次，就画了一个三角形
    # 如果我们需要改变三角形的边长怎么办？
    # 这就要用到变量了，到时候只需改变变量就能改变长度
    # 如果有相同的变量，后面定义的会覆盖前面的
    t.forward(l)
    t.right(120)
    t.forward(l)
    t.right(120)
    t.forward(l)
    t.right(120)

# for 循环
# 循环还有 while 循环，考虑到用不着就不讲了
# 循环用来处理重复的事情
# range() 是一个区间
# range(3) 相当于 0 1 2
# range(5) 相当于 0 1 2 3 4
# i 取的是 range() 里的值，一次取一个，取一次就循环一次
# 冒号后面必有缩进，缩进的代表是同一个代码块
# 照着用就行了，注意一个字符都不能敲错，不能用中文符号
##for i in range(3):
##    t.forward(l)
##    t.right(120)

# 如果想画两个三角形怎么办，再复制一个 for 循环？
# 我们用函数将代码封装起来，到时候直接调用就好了
# def 关键字用来定义函数， triangle 是函数名
# 必须要有冒号接缩进，函数里面也是一个代码块

def triangle():
    global t,l
    for i in range(3):
        t.forward(l)
        t.right(120)
# 函数的调用:triangle()
# 函数可以传递参数进去:
def triangle2(l):
    global t
    for i in range(3):
        t.forward(l)
        t.right(120)

# 需要传递个参数进去才能调用这个函数
# triangle2(250)
# square(100, 150, 100)

# 将画笔定位封装成函数使用，就能有效去除重复代码
def setpen(x, y):
    global t,l
    t.penup()
    t.goto(x, y)
    t.pendown()
    t.setheading(0)

# 定一个函数画长方形
# 写一个画 n 边形的通用函数

def polygon(l, n):
    global t
    angle = 360 / n
    for i in range(n):
         t.forward(l)
         t.right(angle)
# polygon(100, 6)

# 画一个五角星
def five_star(l):
    global t
    for i in range(5):
         t.forward(l)
         t.right(144)
# five_star(100)

# 画一个圆
# 边长在 36 以上就是个圆
def circle():
    global t
    for i in range(36):
         t.forward(10)
         t.right(15)
# circle()

# 在指定的坐标画图
# 比如要在坐标为 (100, 150) 的位置画个正方形
def square(x, y, l):
    global t
    t.penup()
    t.goto(x, y)
    t.pendown()
    for i in range(4):
         t.forward(l)
         t.right(90)

# 画一排正方形，共五个，间隔 10
# 蠢方法
##square(100, 150, 30)
##square(140, 150, 30)
##square(180, 150, 30)
##square(220, 150, 30)
##square(260, 150, 30)

# 使用 for 循环、函数
def square_line(x, y, l, n, dis):
    global t
    for i in range(n):
         inner_x = x + (l + dis) * i
         square(inner_x, y, l)
# square_line(100, 150, 30, 6, 10)

# 画一个正方形方阵
def square_matrix(x, y, l, n, dis, m):
    global t
    for i in range(m):
         inner_y = y - (l + dis) * i
         square_line(x, inner_y, l, n, dis)
# square_matrix(100, 150, 30, 5, 10, 6)

def five_star(l):
    global t
    # fillcolor:填充颜色，给图形上色
    t.fillcolor('yellow')
    t.begin_fill()
    for i in range(5):
         t.forward(l)
         t.right(144)
    t.end_fill()
# five_star(100)

# 抽象画
# for i in range(500):
#      t.forward(i)
#      t.left(90)
# for i in range(500):
#      t.forward(i)
#      t.left(91)

#字典的简单用法
colors = ['red', 'yellow', 'blue', 'green']

# for i in range(500):
#      t.pencolor(colors[i % 4])
#      t.circle(i)
#      t.left(91)
# sides = 5

# colors = ['red', 'yellow', 'blue', 'orange', 'green', 'purple']
# for i in range(360):
#      t.pencolor(colors[i % sides])
#      t.forward(i * 3 / sides + i)
#      t.left(360 / sides + 1)
#      t.width(i * sides / 200)

# 美队盾牌
def circle(x, y, r, color):
    n = 36
    angle = 360 / n
    pi = 3.1415926
    c = 2 * pi * r
    l = c / n
    start_x = x - l / 2
    start_y = y + r
    setpen(start_x, start_y)
    t.pencolor(color)
    t.fillcolor(color)
    t.begin_fill()
    for i in range(n):
         t.forward(l)
         t.right(angle)
    t.end_fill()

def five_star(l):
    setpen(0, 0)
    t.setheading(162)
    t.forward(150)
    t.setheading(0)
    t.fillcolor('WhiteSmoke')
    t.begin_fill()
    t.hideturtle()
    t.penup()
    for i in range(5):
         t.forward(l)
         t.right(144)
    t.end_fill()

def sheild(x,y):
    circle(0, 0, 300, 'red')
    circle(0, 0, 250, 'white')
    circle(0, 0, 200, 'red')
    circle(0, 0, 150, 'blue')
    five_star(284)

def main():
    global scr,t
    draw()
    #等待,直到用户单击鼠标
    scr.onclick(sheild)
    t.write("Click me!",font=("微软雅黑",20))
    turtle.mainloop()

#如果代码作为主程序运行(而不是作为模块导入),则执行主程序
if __name__=="__main__":main()
