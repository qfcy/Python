import pyglet
from pyglet.gl import *
from pyglet.gl.glu import *
from pyglet.window import key

WIDTH=400;HEIGHT=400
cam_x=0;cam_y=0;cam_z=-5

window = pyglet.window.Window(height=HEIGHT, width=WIDTH)

@window.event
def on_draw(): # 注意函数名

    glMatrixMode(GL_PROJECTION);  # 设置当前矩阵为投影矩阵.
    glLoadIdentity();
    # glEnable(GL_DEPTH_TEST)

    # 投影变换.三维变二维
    glFrustum(-5, 5, -5, 5, 2, 1000);  # 透视投影.

    glMatrixMode(GL_MODELVIEW)  # 设置当前矩阵为模型视图矩阵.
    glLoadIdentity()

    glViewport(0, 0, WIDTH,HEIGHT)

    window.clear() # 或 glClear(GL_COLOR_BUFFER_BIT)
    glClear(GL_DEPTH_BUFFER_BIT) # 清除深度(z排序)缓冲区
 
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
def on_key_press(k,m): # 注意函数名称
    global cam_x,cam_y,cam_z
    if k==key.DOWN: # 下
        cam_y-=1
    elif k==key.UP:# 上
        cam_y+=1
    elif k==key.LEFT: # 左
        cam_x-=1
    elif k==key.RIGHT: # 右
        cam_x+=1
    elif k==key.PAGEUP: # page up
        cam_z+=0.5
    elif k==key.PAGEDOWN: # page down
        cam_z-=0.5
    on_draw()

glClearColor(1, 1, 1, 1)
glEnable(GL_DEPTH_TEST) # 开启深度(z排序)
pyglet.app.run()