from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

WIDTH=400;HEIGHT=400
cam_x=0;cam_y=0;cam_z=-5
def init_condition():
    glClearColor(1, 1, 1, 1)  # 定义背景为白色
    #gluOrtho2D(-80, 80, -80, 80)  # 定义xy轴范围
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0,0,-5,0,0,20,0,0,1)
    gluPerspective(60, WIDTH/HEIGHT, 1, 100)

def draw_geometry():
    glClear(GL_COLOR_BUFFER_BIT);
    glLoadIdentity()
 
    #1-视图变换
    gluLookAt(cam_x,cam_y,cam_z,cam_x,cam_y,100000,0,1,0)
    #gluLookAt(4, 0, 1.5, 0, 0, 0, 1, 1, 0);#设置相机位置.
 
    glColor3f(0,0,0);
    #绘制正方体的边
    size = 5.0
    glBegin(GL_LINES);
    #---1---
    glVertex3f(size, size, size);
    glVertex3f(-size, size, size);
    glVertex3f(-size, size, size);
    glVertex3f(-size, -size, size);
    glVertex3f(-size, -size, size);
    glVertex3f(size, -size, size);
    glVertex3f(size, -size, size);
    glVertex3f(size, size, size);
    #---2---
    glVertex3f(size, size, -size);
    glVertex3f(-size, size, -size);
    glVertex3f(-size, size, -size);
    glVertex3f(-size, -size, -size);
    glVertex3f(-size, -size, -size);
    glVertex3f(size, -size, -size);
    glVertex3f(size, -size, -size);
    glVertex3f(size, size, -size);
    #---3---
    glVertex3f(size, size, size);
    glVertex3f(size, -size, size);
    glVertex3f(size, -size, size);
    glVertex3f(size, -size, -size);
    glVertex3f(size, -size, -size);
    glVertex3f(size, size, -size);
    glVertex3f(size, size, -size);
    glVertex3f(size, size, size);
    #---4---
    glVertex3f(-size, size, size);
    glVertex3f(-size, -size, size);
    glVertex3f(-size, -size, size);
    glVertex3f(-size, -size, -size);
    glVertex3f(-size, -size, -size);
    glVertex3f(-size, size, -size);
    glVertex3f(-size, size, -size);
    glVertex3f(-size, size, size);
    glEnd();

    # glBegin(GL_LINE_LOOP)
    # glColor3f(0, 0, 1)
    # glVertex3f(10,10,5)
    # glColor3f(1, 0, 0)
    # glVertex3f(0,10,5)
    # glColor3f(0, 1, 0)
    # glVertex3f(0,0,5)
    # glColor3f(0, 1, 0)
    # glVertex3f(10,0,5)
    # glEnd()
    # #glFlush()
    #
    # glColor3f(0, 0, 0)
    # glBegin(GL_LINE_LOOP)
    # glVertex3f(20,20,20)
    # glVertex3f(0,20,20)
    # glVertex3f(0,0,20)
    # glVertex3f(20,0,20)
    # glEnd()
 
    glFlush()

def onKey(key,x,y):
    global cam_x,cam_y,cam_z
    if key==103: # 下
        cam_y-=1
    elif key==101:# 上
        cam_y+=1
    elif key==100: # 左
        cam_x-=1
    elif key==102: # 右
        cam_x+=1
    elif key==104: # page up
        cam_z+=1
    elif key==105: # page down
        cam_z-=1
    draw_geometry()

def shapeWidget(w, h):
    glMatrixMode(GL_PROJECTION);#设置当前矩阵为投影矩阵.
    glLoadIdentity();
 
    #投影变换.三维变二维
    glFrustum(-5, 5, -5, 5, 2, 1000);#透视投影.
    #glOrtho(-1.0, 1.0, -1.0, 1.0, 2.0, 20.0);
 
    glMatrixMode(GL_MODELVIEW)#设置当前矩阵为模型视图矩阵.
 
    glViewport(0, 0, w, h)

glutInit()  # 启动glut
glutInitDisplayMode(GLUT_SINGLE | GLUT_RGBA)
glutInitWindowSize(WIDTH, HEIGHT)
glutCreateWindow(b"OpenGL\xb3\xcc\xd0\xf2")  # 设定窗口标题, ansi编码
glutDisplayFunc(draw_geometry)  # 调用函数绘制
glutKeyboardFunc(onKey)
glutSpecialFunc(onKey)
glutReshapeFunc(shapeWidget)
glClearColor(1, 1, 1, 1)
glutMainLoop()