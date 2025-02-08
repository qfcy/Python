**文章未经作者授权，禁止转载。**
@[TOC](目录)

在正式开始之前，先看这两张动图：
1.不断减速地球，地球神秘落入太阳中，却自己弹出来？
![](https://img-blog.csdnimg.cn/69ef2a3fef3b4b3198b292d427e51f42.gif#pic_center=x320)
2.不断增加月球到地球的距离，月球受太阳潮汐力影响，脱离地球？
![](https://img-blog.csdnimg.cn/3b8256294fae45cca841577167394dca.gif#pic_center =x380)
这是一个Python计算机模拟万有引力、太阳系行星运动的程序，
应用了万有引力等相关的物理公式计算，可以模拟出天体的椭圆轨道，
以及验证开普勒三大定律，第一、第二宇宙速度。
项目源代码：[gitcode.net/qfcy_/python-gravity-simulation](https://gitcode.net/qfcy_/python-gravity-simulation)
## 1. 算法设计
真刀真枪地开始编程前，研究真实的物理问题，首先要对物理问题涉及的研究对象进行抽象与建模。
在真实的宇宙中，天体与其他各个天体之间都存在引力。
为简化研究，程序使用“降维”的思想，将真实的三维宇宙转换为二维的宇宙。
宇宙的本身属性引力常量G使用一个常量表示。每一个行星可以表示为它的质量、速度、x坐标、y坐标的属性。
**天体加速度的计算**
假设有两个天体A，B，
则引力为F = GMm/r^2^ ，天体之间的距离为 d=sqrt( (x~A~-x~B~)^2^+(y~A~-y~B~)^2^)，天体A在x方向上的加速度为a~x~ = F/m = F |x~A~ - x~B~| /md，在y方向上的加速度为a~y~ = F/m = F |y~A~ - y~B~| /md。
设程序单步经历的时间为t，则新一轮天体A速度v=v~0~+at，位移x=x~0~+vt。

程序这样重复这一个计算，不断地循环，就能逼真地模拟天体的运动过程。t越小，模拟越精确。

## 2. 主程序实现
程序首先初始化屏幕、恒星和各个行星，
然后重复一个不断计算和绘制的**循环**。在这个循环中：
1.计算行星受到重力合力的加速度。
2.计算速度和位移。
3.重复1、2步骤若干次。
4.绘制行星到屏幕上。

流程图大概是这个样子：
![](https://img-blog.csdnimg.cn/e26c44603aa04ad2a0e1d3c7882018f1.png#pic_center =x330)

在程序中，`Star`类对应每个行星，有质量、速度、x坐标、y坐标等属性。
定义`Star`类的代码：
```py
import math
from turtle import *

G = 50 # 引力常量
d_t = 0.00006 # 一轮计算经过的"时间", 经测试说明越小越精确
speed = 10 # 刷新一次屏幕之前执行计算的次数, 越大越快
lst=[]

class Star(Turtle):
    def __init__(self, mass, position, velocity):
        super().__init__()
        self.shape("circle")
        self.m=mass # 行星质量
        self.x,self.y=position # 行星初始位置
        self.dx,self.dy=velocity # 行星初始速度
        self.ax=self.ay=0  # 行星加速度
        lst.append(self)
        self.penup()
        self.setpos((self.x,self.y))
        self.pendown()
    def gravity(self):
        # 计算行星自身受到的加速度，以及列表中位于自己之后的行星受到自己引力的加速度
        for i in range(lst.index(self)+1, len(lst)):
            p=lst[i] # 另一个行星
            dx=p.x-self.x
            dy=p.y-self.y

            d = math.hypot(dx,dy) # 相当于 (dx**2 + dy**2)再开根号
            f = G * self.m * p.m / d**2
            # 将力正交分解为水平、竖直方向并计算加速度
            self.ax+=f / self.m * dx / d
            self.ay+=f / self.m * dy / d
            p.ax-=f / p.m * dx / d
            p.ay-=f / p.m * dy / d
    def step(self):
        # 计算行星速度、位移
        self.dx += d_t*self.ax
        self.dy += d_t*self.ay

        self.x+= d_t*self.dx
        self.y+= d_t*self.dy
    def update(self):
        self.setpos((self.x,self.y))

class Sun(Star): # 太阳固定在中心, 继承自Star类
    def gravity(self):
        for i in range(lst.index(self)+1, len(lst)):
            p=lst[i] # 另一个行星
            dx=p.x-self.x
            dy=p.y-self.y

            d = math.hypot(dx,dy)
            f = G * self.m * p.m / d**2
            # 将力正交分解为水平、竖直方向并计算加速度
            p.ax-=f / p.m * dx / d
            p.ay-=f / p.m * dy / d
    def step(self):
        pass
```
图形界面的实现和主程序循环，使用了`turtle`库：
```py
def clear_screen(x,y): # 清除行星轨迹
    for p in lst:
        p.clear()

scr=Screen()
scr.title("Python 天体引力模拟的探索")
scr.bgcolor("black")
scr.tracer(0,0)
scr.onclick(clear_screen) #点击屏幕清屏

sun = Sun(1e6, (0,0), (0,0))
sun.penup()
sun.color("yellow")
sun.shapesize(2)

earth = Star(1e4, (260,0), (0,400))
earth.color("blue")
earth.shapesize(0.7)

moon = Star(1,(269,0), (0,600))
moon.color("gray")
moon.shapesize(0.5)

t = 0 # 程序运行的总"时间"
while True:
    # 计算行星的位置
    for i in range(speed):
        t += d_t
        # 分别计算每个行星受到的加速度
        for p in lst:
            p.gravity()
        # 根据计算的加速度, 求出速度和位移
        for p in lst:
            p.step()
        for p in lst:
            p.ax=p.ay=0 # 重置加速度
    # 刷新行星
    for p in lst:
        p.update()
    update()
```
## 3. 验证开普勒第一定律
开普勒行星运动第一定律是指：
1.每一行星沿各自的椭圆轨道环绕太阳。
2.太阳则处在椭圆的一个焦点上。

这里程序检验**行星的轨道是否符合椭圆的方程**：
椭圆上的任意一点到两个焦点的距离之和为一个定值，等于它的长轴。根据这个性质，设P为行星，F1、F2为焦点，太阳位于F1上，如果PF1+PF2近似等于长轴2a，则验证通过。
 ![](https://img-blog.csdnimg.cn/34b8b70611cb4ecf923a31ae1b5790c3.png#pic_center)
在前面计算和绘制的事件循环中，每一次循环结束之后，增加计算一次PF1+PF2和2a，执行验证定律的代码。流程图大概是这个样子：
![](https://img-blog.csdnimg.cn/54f5acfe31ef454d9e1fc0d7d0eb9b08.png#pic_center =x330)

新建一个py文件，输入前文导入模块、定义常量、创建`Star`和`Sun`类的代码，以及以下代码: 
```py
def get_orbit_shape(): # 获取椭圆轨道的长轴长度2a，及焦点F2坐标
    max_x=max(x_lst)
    min_x=min(x_lst)
    middle = (max_x + min_x)/2 # 椭圆中心X坐标，焦点F1是太阳(0,0)，X是F1F2的中点
    return max_x-min_x,2 * middle - 0

def clear_screen(x,y): # 清除行星轨迹
    for p in lst:
        p.clear()

scr=Screen()
scr.title("Python 天体引力模拟的探索")
scr.bgcolor("black")
scr.tracer(0,0)
scr.onclick(clear_screen) #点击屏幕清屏

sun = Sun(1e6，(0,0)，(0,0)) # 恒星
sun.penup()
sun.color("yellow")
sun.shapesize(2)

p = Star(1e4，(260,0)，(0,300)) # 行星
p.color("blue")
p.shapesize(0.7)

t = 0 # 程序运行的总"时间"
while True:
    # 计算行星的位置
    for i in range(speed):
        t += d_t
        # 分别计算每个行星受到的加速度
        for p in lst:
            p.gravity()
        # 根据计算的加速度，求出速度和位移
        for p in lst:
            p.step()
        for p in lst:
            p.ax=p.ay=0 # 重置加速度

    # 刷新行星
    for p in lst:
        p.update()
    update()

    # 验证椭圆轨道
    if t < 1:
        x_lst.append(p.x)
    else:
        _2a,x_f2 = get_orbit_shape()
        d = math.hypot(p.x,p.y) # 行星到恒星距离
        d2 = math.hypot(x_f2-p.x,p.y) # 行星到焦点F2距离
        print("PF1 + PF2:",d+d2，"2a:",_2a) # 如果PF1+PF2近似等于2a，则验证通过
```
运行效果：左侧可以看到程序的输出中，PF1+PF2近似等于2a，符合椭圆的定义。这近乎完美地说明了行星的轨道是椭圆。
![](https://img-blog.csdnimg.cn/3fff91a686c6472baea25e5b766fcc02.png#pic_center =x250)
## 4. 验证开普勒第二定律

开普勒行星运动第二定律，指的是太阳系中太阳和运动中的行星的连线（矢径）在相等的时间内扫过相等的面积。

验证定律的代码，将行星轨道扫过的部分分割成一个个三角形，分别计算每个三角形面积，再累加得到行星轨道扫过的面积S，并除以经过的时间t。**如果S/t是一个定值，则验证通过**。

流程图大概是这个样子：
![](https://img-blog.csdnimg.cn/82a1b2b691314bda9bc2aac8cc213c78.png#pic_center =x380)

图 5 对应流程图
新建一个py文件，输入前文导入模块、定义常量、创建`Star`和`Sun`类的代码，并添加以下代码: 
```py
def calc_square(a,b,c): # 根据边长计算三角形面积
    p = (a+b+c)/2
    return math.sqrt(p*(p-a)*(p-b)*(p-c))

def clear_screen(x,y): # 清除行星轨迹
    for p in lst:
        p.clear()

scr=Screen()
scr.title("Python 天体引力模拟的探索")
scr.bgcolor("black")
scr.tracer(0,0)
scr.onclick(clear_screen) #点击屏幕清屏

sun = Sun(1e6，(0,0)，(0,0))
sun.penup()
sun.color("yellow")
sun.shapesize(2)

p = Star(1e4，(260,0)，(0,300))
p.color("blue")
p.shapesize(0.7)

t = 0 # 程序运行的总"时间"
S = 0 # 累计扫过面积
prev_x，prev_y = 260,0 # 行星的前一个坐标
while True:
    # 计算行星的位置
    for i in range(speed):
        t += d_t
        # 分别计算每个行星受到的加速度
        for p in lst:
            p.gravity()
        # 根据计算的加速度，求出速度和位移
        for p in lst:
            p.step()
        for p in lst:
            p.ax=p.ay=0 # 重置加速度
    # 刷新行星
    for p in lst:
        p.update()
    update()

    # 累加轨道扫过的图形面积
    # 算出3条边
    a = math.hypot(p.x-prev_x，p.y-prev_y)
    b = math.hypot(p.x，p.y)
    c = math.hypot(prev_x，prev_y)
    S += calc_square(a,b,c)
    print("时间:%.4f"%t，"行星扫过面积:%.4f"%S,
          "行星扫过面积÷时间 = %.4f"%(S/t))# 如果行星扫过面积÷时间 是一个定值，则验证通过
prev_x，prev_y = p.x,p.y
```
运行效果：行星扫过面积÷时间近乎为一个定值，验证了开普勒第二定律。
![](https://img-blog.csdnimg.cn/bc6b0727a9054ae8b27db4cc246f3faf.png#pic_center =x250)

## 5. 验证开普勒第三定律
开普勒第三定律，指绕同一天体公转的行星，椭圆轨道半长轴a的立方与周期T的平方之比是一个常量。
也就是 a ^3^ / T ^2^ = k 。

程序把每次行星和太阳连线的角度放入列表`a_lst`，根据两次角度为0°的时间差，得出行星的周期；
将每次行星和太阳距离放入列表`d_lst`，再根据`d_lst`的最大值和最小值，得出行星轨道的半长轴。
然后计算 a ^3^ / T ^2^，如果结果是一个定值，则验证通过。

新建文件，输入前文导入模块、定义常量、创建`Star`和`Sun`类的代码，并添加以下代码: 
```py
def get_orbit_shape():
    max_d=max(d_lst)
    min_d=min(d_lst)
    return (max_d + min_d)/2

def clear_screen(*_): # 清除行星轨迹
    for p in lst:
        p.clear()

scr=Screen()
scr.title("Python 天体引力模拟的探索 - 开普勒第三定律演示")
scr.bgcolor("black")
scr.tracer(0,0)
scr.onclick(clear_screen) #点击屏幕清屏

w=Turtle() # w 用于输出文字
w.penup();w.hideturtle()
w.color("white") # 设置文字颜色为白色
w.goto(scr.window_width()//2-260,
             scr.window_height()//2-60)
w.write("生成结果中 ...", font=(None,12))

sun = Sun(1e6, (0,0), (0,0))
sun.penup()
sun.color("yellow")
sun.shapesize(2)

earth = Star(1e4, (260,0), (0,400))
earth.color("blue")
earth.shapesize(0.7)


t = 0 # 程序运行的总"时间"
t_start=0 # 连线的角度为0°时的"时间"
d_lst=[] # 存储行星和太阳距离
a_lst=[0,0] # 存储行星和太阳连线的角度
while True:
    # 计算行星的位置
    for i in range(speed):
        t += d_t
        # 分别计算每个行星受到的加速度
        for p in lst:
            p.gravity()
        # 根据计算的加速度, 求出速度和位移
        for p in lst:
            p.step()
        for p in lst:
            p.ax=p.ay=0 # 重置加速度
    try:
        # 刷新行星
        for p in lst:
            p.update()
        update()
    

        d_lst.append(math.hypot(sun.x-earth.x,sun.y-earth.y))
        a_lst.append(math.atan2(sun.y-earth.y,earth.x-sun.x)) # atan2(y, x)
        if a_lst[-2] > 0 and a_lst[-1]<=0:
            T = t - t_start # 轨道周期
            t_start = t
            a = get_orbit_shape()

            # 输出文字
            w.clear()
            w.goto(scr.window_width()//2-260,
                 scr.window_height()//2-60)
            w.write("a^3=%.4f" % a**3 + "\nT^2=%.4f" % T**2 + \
              "\nk = %.4f" % (a**3/T**2), font=(None,12))
            # 清除列表
            d_lst.clear()
            a_lst=[0,0]
    except (Terminator,tk.TclError):break # 如果窗口已关闭，忽略错误
```
运行效果：
![](https://img-blog.csdnimg.cn/5c32eba653f04b8ea1e9fb18253bbb8d.png#pic_center =x300)

## 6. 验证第一、二宇宙速度
程序首先通过公式，获取行星的第一宇宙速度，然后乘以sqrt(2)得到第二宇宙速度。

流程图是这样：
  ![](https://img-blog.csdnimg.cn/bca60d98ffb14779bbadc318364f4d3d.png#pic_center =x330)
打开编辑器，新建一个py文件，输入之前导入模块、定义常量、创建Star和Sun类的代码，以及以下代码: 
```py
def clear_screen(x,y): # 清除行星轨迹
    for p in lst:
        p.clear()
scr=Screen()
scr.title("Python 天体引力模拟的探索")
scr.bgcolor("black")
scr.tracer(0,0)
scr.onclick(clear_screen) #点击屏幕清屏
sun = Sun(1e6，(0,0)，(0,0))
sun.penup()
sun.color("yellow")
sun.shapesize(2)

# 测试第一、第二宇宙速度
r = 20
print('"太阳"半径:'，r)
print('"太阳"的第一宇宙速度:'，sun.getOrbitSpeed(r))
test = Star(1,(20,0)，(0，sun.getOrbitSpeed(r))) # 检验第一宇宙速度
test.color("red")
test.shapesize(0.4)
print('"太阳"的第二宇宙速度:'，sun.getOrbitSpeed(r)*math.sqrt(2)) # 第一宇宙速度的√2倍
test2 = Star(1,(0，-20)，(sun.getOrbitSpeed(r)*math.sqrt(2)，0)) # 检验第二宇宙速度，观察到test2的轨迹是抛物线
test2.color("purple")
test2.shapesize(0.4)

t = 0 # 程序运行的总"时间"
while True:
    # 计算行星的位置
    for i in range(speed):
        t += d_t
        # 分别计算每个行星受到的加速度
        for p in lst:
            p.gravity()
        # 根据计算的加速度，求出速度和位移
        for p in lst:
            p.step()
        for p in lst:
            p.ax=p.ay=0 # 重置加速度
    # 刷新行星
    for p in lst:
        p.update()
    update()
```
运行效果：可以观察到，第一宇宙速度的天体沿着圆轨道运行，而第二宇宙速度的天体则沿着抛物线飞出。
 ![](https://img-blog.csdnimg.cn/160aba10d5594fc1b66b035fce0c8f83.png#pic_center =x360)

## 7. 总结
这个程序是一次计算机模拟，利用了计算机运算速度快的优势，模拟宇宙中天体的运动。
程序的编写运用了以下思想方法，可以为编程研究其他的物理问题提供参考：
**（一）抽象与建模**
程序使用了面向对象编程的方法，对研究对象进行了建模。
在真实的宇宙中，天体与其他各个天体之间都存在引力。宇宙的本身属性引力常量G使用一个常量表示。程序中定义了Star类，对应每个行星，具有质量、速度、x坐标、y坐标等属性；并将所有的Star类实例放入一个列表lst中，便于在主程序中调用。
**（二）重复迭代**
	如前面所述，程序重复一个不断计算和绘制的事件循环，每轮循环中先计算行星受到的引力合力，再计算加速度、速度、位移。重复迭代成千上万次，就能将行星运动的轨迹曲线细腻地模拟出来。

看到这里，记得==点赞==、==收藏==。
项目源代码：[gitcode.net/qfcy_/python-gravity-simulation](https://gitcode.net/qfcy_/python-gravity-simulation)

*注: 程序灵感来自Python标准库中的turtledemo\planet_and_moon.py*

**声明：本文为作者qfcy的原创文章。==文章未经作者授权，禁止转载。==**


