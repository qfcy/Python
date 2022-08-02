import pyglet
from pyglet.gl import *
from pyglet.gl.glu import *
from pyglet.window import key
import math
from random import randint

WIDTH=400;HEIGHT=400
angle_xy = math.pi / 2 # X-Y平面内的相机角度, 弧度制(0-360°变为0-2π)
angle_z = 0 # 相机与中心点O连线与X-Y平面的夹角, 弧度制
distance = 20
centerx,centery,centerz = 38,9, -11 # 中心点O位置
data = [(3.2045, 50.7902), (2.3187, 50.2312), (1.5227, 49.5507), (0.8231, 48.7698), (0.2268, 47.9115), (-0.2594, 46.9998), (-0.6292, 46.0584), (-0.8766, 45.1107),
        (-0.9964, 44.1779), (-0.9845, 43.279), (-0.8378, 42.4295), (-0.7134, 42.0271), (-0.5548, 41.6411), (-0.3619, 41.2725), (-0.1348, 40.9221), (0.1265, 40.5905),
        (0.4219, 40.2782), (1.1146, 39.7128), (1.9425, 39.2276), (2.9045, 38.8233), (4.0, 38.5), (2.9045, 38.1766), (1.9424, 37.7722), (1.1146, 37.287),
        (0.4218, 36.7216), (0.1264, 36.4093), (-0.1349, 36.0778), (-0.362, 35.7274), (-0.5548, 35.3589), (-0.7134, 34.973), (-0.8378, 34.5706), (-0.9844, 33.7212),
        (-0.9964, 32.8226), (-0.8765, 31.8901), (-0.6291, 30.9425), (-0.2593, 30.0015), (0.227, 29.09), (0.8233, 28.2319), (1.5229, 27.4513), (2.319, 26.771),
        (3.2048, 26.2122), (4.1739, 25.7935), (5.2203, 25.5298), (6.3384, 25.4326), (7.5231, 25.5104), (8.77, 25.769), (10.0749, 26.2121), (11.4344, 26.8415),
        (12.8454, 27.6578), (14.3053, 28.6604), (15.812, 29.848), (17.3638, 31.2189), (18.9593, 32.7712), (20.5975, 34.5031), (22.2779, 36.4131), (24.0, 38.5),
        (22.2778, 40.5874), (20.5974, 42.4978), (18.9591, 44.2302), (17.3636, 45.7829), (15.8118, 47.1541), (14.3051, 48.342), (12.8451, 49.3448), (11.4341, 50.1612),
        (10.0746, 50.7907), (8.7697, 51.2338), (7.5228, 51.4924), (6.3381, 51.5702), (5.22, 51.4729)] # 心的矢量图数据
z1=8; z2=10 # 心两个面的z坐标

def convert_pos():
    # 将相机角度转换为相机的X,Y,Z坐标
    if math.pi/2 < angle_z < math.pi * 1.5:
        angle_xy2 = angle_xy + math.pi
        flag = -1
    else:
        angle_xy2 = angle_xy
        flag = 1
    cam_x=math.cos(angle_xy2)*distance *math.cos(angle_z) + centerx
    cam_y=math.sin(angle_xy2)*distance *math.cos(angle_z) + centery
    cam_z=math.sin(angle_z)*distance + centerz
    return cam_x,cam_y,cam_z,flag

def draw_heart(dx,dy,dz):
    # dx, dy, dz为心从中心点向X, Y, Z轴正方向平移多少
    # 顶、底面
    glBegin(GL_POLYGON)
    glColor3f(1, 0, 1)
    for x, y in data:
        glVertex3f(y+dx, z1+dy, -x+dz)
    glEnd()
    glBegin(GL_POLYGON)
    for x, y in data:
        glVertex3f(y+dx, z2+dy, -x+dz)
    glEnd()
    # 绘制侧面
    glColor3f(0.5, 0, 0.5)
    for i in range(len(data)):
        if i + 1 == len(data):  # 超出范围
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
def on_draw(): # 注意函数名, 必须是on_draw

    glMatrixMode(GL_PROJECTION);  # 设置当前矩阵为投影矩阵.
    glLoadIdentity();
    # glEnable(GL_DEPTH_TEST)

    # 投影变换.三维变二维
    glFrustum(-5, 5, -5, 5, 2, 1000);  # 透视投影.

    glMatrixMode(GL_MODELVIEW)  # 设置当前矩阵为模型视图矩阵.
    glLoadIdentity()

    glViewport(0, 0, WIDTH,HEIGHT)

    window.clear() # 或 glClear(GL_COLOR_BUFFER_BIT)
    glClear(GL_DEPTH_BUFFER_BIT) # 清除深度缓冲区
 
    # 改变相机位置和角度
    cam_x,cam_y,cam_z,flag = convert_pos()
    gluLookAt(cam_x,cam_y,cam_z,centerx,centery,centerz,0,0,flag) # 0,0,1为相机朝上方向, 这里是z轴

    for dx,dy,dz in lst_pos:
        draw_heart(dx,dy,dz)

    glFlush()

@window.event
def on_key_press(k,m): # 注意函数名, 必须是on_draw才能在绘制时被回调
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
        distance/=1.1
    elif k==key.PAGEDOWN: # page down
        distance*=1.1
    angle_z %= math.pi*2
    on_draw()

lst_pos = [(0,0,0)]
for i in range(25):
    lst_pos.append((randint(-200,200),randint(-200,200),randint(-200,200)))
glClearColor(0.8, 1, 1, 1)
glEnable(GL_DEPTH_TEST) # 开启深度(z排序)
pyglet.app.run()