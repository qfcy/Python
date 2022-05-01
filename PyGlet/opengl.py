import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

def init_condition():
    glClearColor(1.0, 1.0, 1.0, 1.0)  # 定义背景为白色
    gluOrtho2D(-8.0, 8.0, -8.0, 8.0)  # 定义xy轴范围
def render():
    pass
def draw_geometry():
    glClear(GL_COLOR_BUFFER_BIT)
    glColor3f(0, 1.0, 1.0)  # 设定颜色RGB
    glBegin(GL_POLYGON)
    #glVertex2f(-2, 2)
    #glVertex2f(-2, 5)
    #glVertex2f(-5, 5)
    #glVertex2f(-5, 2)

    glColor3f(5,5,5)
    glVertex3f(-5,-5,0.0)
    glColor3f(0, 5, 0)
    glVertex3f(0, -5, 0)
    glColor3f(0, 0, 5)
    glVertex3f(0, 5, 0)
    glColor3f(0, 3, 2)
    glVertex3f(0, 10, 5)

    glEnd()
    glFlush()  # 执行绘图

glutInit()  # 启动glut
glutInitDisplayMode(GLUT_SINGLE | GLUT_RGBA)
glutInitWindowSize(400, 400)
glutCreateWindow(b"Hello OpenGL")  # 设定窗口标题
glutDisplayFunc(draw_geometry)  # 调用函数绘制
init_condition()  # 设定背景
glutMainLoop()