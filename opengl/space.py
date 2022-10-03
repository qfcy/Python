import pyglet
from pyglet.gl import *
from pyglet.gl.glu import *
from OpenGL.GLUT import *
from pyglet.window import key
import math
from random import random, randint

angle_xy = math.pi / 2 # X-Y平面内的相机角度, 弧度制(0-360°变为0-2π)
angle_z = 0 # 相机绕Z轴旋转的角度
distance = 100
radius = 5 # 球体半径
centerx,centery,centerz = radius,radius,radius # 中心点位置, 相机绕中心点旋转

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

def draw_sphere(dx,dy,dz,color): # 绘制球体
    # dx, dy, dz为球体从中心点向X, Y, Z轴正方向平移多少
    # 绘制顶、底面
    glColor3f(*color) # 随机生成颜色
    glPushMatrix()
    glTranslatef(dx+radius, dy+radius, dz+radius)
    glutSolidSphere(radius,40,40)
    glPopMatrix()

window = pyglet.window.Window(fullscreen=True)
WIDTH,HEIGHT = window.width, window.height # 获取屏幕分辨率
@window.event
def on_draw(): # 注意函数名, 必须是on_draw才能绑定这个事件

    glMatrixMode(GL_PROJECTION)  # 设置当前矩阵为投影矩阵
    glLoadIdentity()

    # 透视投影, 前4个参数类似游戏中的FOV(视角大小), 
    # 后2个参数分别是物体与相机的最近、最远距离
    glFrustum(-2, 2, -2*HEIGHT/WIDTH, 2*HEIGHT/WIDTH, 2, 30000)

    glMatrixMode(GL_MODELVIEW)  # 设置当前矩阵为模型视图矩阵
    glLoadIdentity()

    glViewport(0, 0, WIDTH,HEIGHT)

    window.clear() # 或 glClear(GL_COLOR_BUFFER_BIT)
    glClear(GL_DEPTH_BUFFER_BIT) # 清除深度(z排序)缓冲区
 
    # 改变相机位置和角度
    cam_x,cam_y,cam_z,flag = convert_pos()
    gluLookAt(cam_x,cam_y,cam_z,centerx,centery,centerz,0,0,flag) # 0,0,flag为相机朝上方向

    for pos, color in lst_pos: # 绘制列表中的各个球体
        draw_sphere(*pos,color)

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
    angle_xy -= dx / 100
    angle_z -= dy / 100
    angle_z %= math.pi * 2
    on_draw()

@window.event
def on_mouse_scroll(x,y, _, d):
    global distance
    distance /= 1.1**d
    on_draw()

glutInit()
# 中心的球体
light = 0.5 + random() * 0.5 # 亮度
lst_pos = [((0,0,0),(light,light,light))]
for i in range(50): # 随机生成多个球体
    light = 0.2 + random() * 0.8  # 亮度
    lst_pos.append(((randint(-500,500),randint(-500,500),randint(-500,500)),
                    (light,light,light)))
glClearColor(0, 0, 0, 1)
glEnable(GL_DEPTH_TEST) # 开启深度(z排序), 使程序支持近的物体遮挡远的物体
pyglet.app.run()
