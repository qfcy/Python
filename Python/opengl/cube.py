from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

WIDTH=400;HEIGHT=400
cam_x=0;cam_y=0;cam_z=-5

def draw_geometry():
    glClear(GL_COLOR_BUFFER_BIT)
    glClear(GL_DEPTH_BUFFER_BIT) # 清除深度(z排序)缓冲区
    glLoadIdentity()
 
    #1-视图变换
    gluLookAt(cam_x,cam_y,cam_z,cam_x,cam_y,100000,0,1,0)

    # 顶、底面
    glColor3f(0.5, 0.5, 1)
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
        cam_z+=0.5
    elif key==105: # page down
        cam_z-=0.5
    draw_geometry()

def shapeWidget(w, h):
    glMatrixMode(GL_PROJECTION) #设置当前矩阵为投影矩阵
    glLoadIdentity()
    #glEnable(GL_DEPTH_TEST)
 
    # 透视投影, 类似游戏中的FOV(视角大小)
    glFrustum(-5, 5, -5, 5, 2, 1000)
 
    glMatrixMode(GL_MODELVIEW)  # 模型视图矩阵
 
    glViewport(0, 0, w, h)

glutInit()  # 启动glut
# GLUT_MULTISAMPLE为抗锯齿
glutInitDisplayMode(GLUT_SINGLE | GLUT_RGBA | GLUT_MULTISAMPLE)
glutInitWindowSize(WIDTH, HEIGHT)
glutCreateWindow("OpenGL程序".encode("ansi"))  # 设定窗口标题, ansi编码
glutDisplayFunc(draw_geometry)  # 调用函数绘制
glutKeyboardFunc(onKey)
glutSpecialFunc(onKey)
glutReshapeFunc(shapeWidget)
glClearColor(1, 1, 1, 1)
glEnable(GL_DEPTH_TEST) # 开启深度(z排序)
glutMainLoop()