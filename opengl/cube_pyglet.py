import pyglet
from pyglet.gl import *
from pyglet.gl.glu import *

WIDTH=400;HEIGHT=400
cam_x=0;cam_y=0;cam_z=-5

window = pyglet.window.Window(height=HEIGHT, width=WIDTH)

@window.event
def on_draw(): # 注意函数名
    window.clear()
    glMatrixMode(GL_PROJECTION);  # 设置当前矩阵为投影矩阵.
    glLoadIdentity();
    # glEnable(GL_DEPTH_TEST)

    # 投影变换.三维变二维
    glFrustum(-5, 5, -5, 5, 2, 1000);  # 透视投影.

    glMatrixMode(GL_MODELVIEW)  # 设置当前矩阵为模型视图矩阵.
    glLoadIdentity()

    glViewport(0, 0, WIDTH,HEIGHT)

    glClear(GL_COLOR_BUFFER_BIT)
    glClear(GL_DEPTH_BUFFER_BIT) # 清除深度缓冲区
 
    # 改变相机位置和角度
    gluLookAt(cam_x,cam_y,cam_z,cam_x,cam_y,100000,0,1,0)

    # 顶、底面
    glColor3f(0.5,0.5,1)
    glBegin(GL_POLYGON)
    glVertex3f(10,10,10)
    glVertex3f(0,10,10)
    glVertex3f(0,0,10)
    glVertex3f(10,0,10)
    glEnd()

    glColor3f(0.5, 1, 0)
    glBegin(GL_POLYGON)
    glVertex3f(10, 10, 0)
    glVertex3f(0, 10, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(10, 0, 0)
    glEnd()
    # 4个侧面
    glColor3f(1, 0.5, 1)
    glBegin(GL_POLYGON)
    glVertex3f(10, 0, 10)
    glVertex3f(0, 0, 10)
    glVertex3f(0, 0, 0)
    glVertex3f(10, 0, 0)
    glEnd()

    glColor3f(0.5, 1, 1)
    glBegin(GL_POLYGON)
    glVertex3f(10, 10, 10)
    glVertex3f(0, 10, 10)
    glVertex3f(0, 10, 0)
    glVertex3f(10, 10, 0)
    glEnd()

    glColor3f(0.8, 0.5, 1)
    glBegin(GL_POLYGON)
    glVertex3f(10, 10, 10)
    glVertex3f(10, 10, 0)
    glVertex3f(10, 0, 0)
    glVertex3f(10, 0, 10)
    glEnd()

    glColor3f(1, 0.5, 0.5)
    glBegin(GL_POLYGON)
    glVertex3f(0, 10, 10)
    glVertex3f(0, 10, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 0, 10)
    glEnd()

    glFlush()

@window.event
def on_key_press(key,m): # 注意函数名称
    global cam_x,cam_y,cam_z
    if key==65362: # 下
        cam_y-=1
    elif key==65364:# 上
        cam_y+=1
    elif key==65361: # 左
        cam_x-=1
    elif key==65363: # 右
        cam_x+=1
    elif key==65365: # page up
        cam_z+=0.5
    elif key==65366: # page down
        cam_z-=0.5
    on_draw()

glClearColor(1, 1, 1, 1)
glEnable(GL_DEPTH_TEST) # 开启深度(z排序)
pyglet.app.run()