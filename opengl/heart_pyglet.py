import pyglet
from pyglet.gl import *
from pyglet.gl.glu import *
from pyglet.window import key
import math
from random import random, randint

WIDTH=400;HEIGHT=400
angle_xy = math.pi / 2 # X-Y平面内的相机角度, 弧度制(0-360°变为0-2π)
angle_z = 0 # 相机绕Z轴旋转的角度
distance = 20
centerx,centery,centerz = 38,9, -11 # 中心点位置, 相机绕中心点旋转
data = [(3.2045, 50.7902), (1.5227, 49.5507), (0.2268, 47.9115), (-0.6292, 46.0584), (-0.9964, 44.1779), (-0.8378, 42.4295), (-0.5548, 41.6411), (-0.1348, 40.9221),
        (0.4219, 40.2782), (1.9425, 39.2276), (2.9045, 38.8233), (4.0, 38.5), (2.9045, 38.1766), (1.9424, 37.7722), (0.4218, 36.7216), (-0.1349, 36.0778), (-0.5548, 35.3589), (-0.8378, 34.5706), (-0.9964, 32.8226),
        (-0.6291, 30.9425), (0.227, 29.09), (1.5229, 27.4513), (3.2048, 26.2122), (5.2203, 25.5298), (7.5231, 25.5104), (10.0749, 26.2121), (12.8454, 27.6578), (15.812, 29.848),
        (18.9593, 32.7712), (22.2779, 36.4131), (24.0, 38.5), (22.2778, 40.5874), (18.9591, 44.2302), (15.8118, 47.1541), (12.8451, 49.3448), (10.0746, 50.7907),
        (7.5228, 51.4924), (5.22, 51.4729)]# 心形的矢量图数据
z1=8; z2=10 # 心形两个面的z坐标

def convert_pos():
    # 将相机角度转换为相机的X,Y,Z坐标
    if math.pi/2 < angle_z < math.pi * 1.5:
        flag = -1 # 相机朝下
    else:
        flag = 1 # 相机朝上
    cam_x=math.cos(angle_xy)*distance *math.cos(angle_z) + centerx
    cam_y=math.sin(angle_xy)*distance *math.cos(angle_z) + centery
    cam_z=math.sin(angle_z)*distance + centerz
    return cam_x,cam_y,cam_z,flag

def draw_heart(dx,dy,dz): # 绘制心形
    # dx, dy, dz为心形从中心点向X, Y, Z轴正方向平移多少
    # 绘制顶、底面
    glBegin(GL_POLYGON)
    glColor3f(random()*0.5+0.5, 0, random()*0.5+0.5) # 随机生成颜色
    for x, y in data:
        glVertex3f(y+dx, z1+dy, -x+dz) # 不使用x+dx, y+dy, z1+dz目的是旋转心形, 使心形更易于查看
    glEnd()
    glBegin(GL_POLYGON)
    for x, y in data:
        glVertex3f(y+dx, z2+dy, -x+dz)
    glEnd()
    # 绘制侧面
    glColor3f(0.5, 0, 0.5)
    for i in range(len(data)):
        if i + 1 == len(data):  # 下一个点超出索引范围
            next_point = data[0]
        else:
            next_point = data[i + 1]
        point = data[i]
        glBegin(GL_POLYGON)
        glVertex3f(point[1]+dx, z1+dy, -point[0]+dz)
        glVertex3f(next_point[1]+dx, z1+dy, -next_point[0]+dz)
        glVertex3f(next_point[1]+dx, z2+dy, -next_point[0]+dz)
        glVertex3f(point[1]+dx, z2+dy, -point[0]+dz)
        glEnd()

window = pyglet.window.Window(height=HEIGHT, width=WIDTH)

@window.event
def on_draw(): # 注意函数名, 必须是on_draw才能在绘制时被回调

    glMatrixMode(GL_PROJECTION)  # 设置当前矩阵为投影矩阵.
    glLoadIdentity()

    # 投影变换.三维变二维
    glFrustum(-5, 5, -5, 5, 2, 1000)  # 透视投影.

    glMatrixMode(GL_MODELVIEW)  # 设置当前矩阵为模型视图矩阵.
    glLoadIdentity()

    glViewport(0, 0, WIDTH,HEIGHT)

    window.clear() # 或 glClear(GL_COLOR_BUFFER_BIT)
    glClear(GL_DEPTH_BUFFER_BIT) # 清除深度(z排序)缓冲区
 
    # 改变相机位置和角度
    cam_x,cam_y,cam_z,flag = convert_pos()
    gluLookAt(cam_x,cam_y,cam_z,centerx,centery,centerz,0,0,flag) # 0,0,flag为相机朝上方向

    for dx,dy,dz in lst_pos:
        draw_heart(dx,dy,dz)

    glFlush()

@window.event
def on_key_press(k,_): # 注意函数名
    global angle_xy,angle_z,distance
    if k==key.DOWN: # 下
        angle_z -= math.pi * 1/18 # 10°
    elif k==key.UP:# 上
        angle_z += math.pi * 1/18
    elif k==key.LEFT: # 左
        angle_xy -= math.pi * 1/18
    elif k==key.RIGHT: # 右
        angle_xy += math.pi * 1/18
    elif k==key.PAGEUP: # page up
        distance/=1.15
    elif k==key.PAGEDOWN: # page down
        distance*=1.15
    angle_z %= math.pi*2
    on_draw()

@window.event
def on_mouse_drag(x,y,dx,dy,btn,_):
    global angle_xy, angle_z
    angle_xy += dx / 100
    angle_z -= dy / 100
    angle_z %= math.pi * 2
    on_draw()

@window.event
def on_mouse_scroll(x,y, _, d):
    global distance
    distance /= 1.1**d
    on_draw()

# 随机生成多个心形
lst_pos = [(0,0,0)] # 中心的心形
for i in range(20):
    lst_pos.append((randint(-200,200),randint(-200,200),randint(-200,200)))
glClearColor(0.8, 1, 1, 1)
glEnable(GL_DEPTH_TEST) # 开启深度(z排序)
pyglet.app.run()