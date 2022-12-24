import pyglet
from pyglet.gl import *
from pyglet.window import key

pos = [0, 0, -20]
rot_y = 0

win = pyglet.window.Window(height=500, width=500)

@win.event
def on_draw():

    global pos_z, rot_y
    print('drawing')

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(90, 1, 0.1, 100)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    glTranslatef(*pos)
    glRotatef(rot_y, 0, 1, 0)

    win.clear() # 或glClear(GL_COLOR_BUFFER_BIT)
    gluLookAt(0, 0, 0, -5, -5, 0, 0, 1, 0)

    glBegin(GL_POLYGON)
    glColor3f(0, 1, 1)
    glVertex3f(-5,-5,0)
    glVertex3f(5,-5,0)
    glVertex3f(0,5,0)
    glColor3f(1, 0, 1)
    glVertex3f(5,-5,5)
    glVertex3f(5,-5,-5)
    glEnd()

    glFlush()

@win.event
def on_key_press(s,m):

    global pos_z, rot_y
    if s == key.S:
        pos[2] -= 1
    if s == key.W:
        pos[2] += 1
    if s == key.A:
        rot_y += 5
    if s == key.D:
        rot_y -= 5

glClearColor(1, 1, 0.8, 1)
gluLookAt(4, 2, 4, 0, 0, 0, 0, 1, 0)
pyglet.app.run()
