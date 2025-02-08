# -*- coding: utf-8 -*-
# 黑洞模拟2 & 在turtle屏幕上绘制旋转图片
# 原理：行星绕恒星旋转时，不断减速，行星将会往恒星无限下坠。
# 不断减小引力系统的dt, 使行星下坠时不损失模拟精度。
import sys,os
try:
    import solar_system # 导入主模块
    from solar_system import *
    from solar_system import _copy_func
except ImportError:
    sys.path.append(os.path.join(os.path.split(__file__)[0],"..")) # 避免导入失败
    import __init__ as solar_system;from __init__ import *
    from __init__ import _copy_func

from time import perf_counter
from random import randrange
import math,turtle,pickle
from turtle import *
from tkinter import TclError

try:
    from PIL import Image,ImageTk
    from tkinter import PhotoImage
except ImportError:
    Image=None

__version__="1.3.3"

## -- 重写turtle模块中的函数，在turtle模块源码的基础上加以修改 --
# 由于turtle模块极少更新，修改的函数几乎不会在新版Python中不兼容
images={} # 用于创建图像的引用
def _image(self,filename):
    img=Image.open(filename)
    im = ImageTk.PhotoImage(img)
    im.raw = img
     # 图像的缩放缓存，两项分别是放大倍数和PhotoImage对象，避免重复缩放图片，提高性能
    im.zoomcache = [None,None]
    return im

def _createimage(self, image):
    """Create and return image item on canvas.
    """

    id = self.cv.create_image(0, 0, image=image)
    return id

def _drawimage(self, item, pos, image, angle=None,zoom=None):
    """Configure image item as to draw image object
    at position (x,y) on canvas)
    """
    w=self.window_width();h=self.window_height()
    if not (-h//2 < pos[1] < h//2\
        and -w//2 <= -pos[0] < w//2): # 图像不在屏幕内
        self.cv.itemconfig(item, image=self._blankimage()) # 不绘制
        return
    prev=image
    if zoom:
        if zoom == image.zoomcache[0]:
            image=image.zoomcache[1] # 使用该图像的缩放缓存
        else:
            raw=image.raw
            size=(int(raw.size[0] * zoom), int(raw.size[1] * zoom))
            raw = raw.resize(size,resample=Image.Resampling.BILINEAR)
            image=ImageTk.PhotoImage(raw)
            image.raw=raw # 更新PhotoImage的raw属性
            prev.zoomcache=[zoom,image] # 更新缩放缓存

    if angle is not None:
        
        raw=image.raw
        image=ImageTk.PhotoImage(raw.rotate(angle)) # 旋转一定角度
        image.raw=raw
        
    images[item]=image # 创建image的引用, 防止image被Python垃圾回收而图像无法绘制

    x, y = pos
    self.cv.coords(item, (x * self.xscale, -y * self.yscale))
    self.cv.itemconfig(item, image=image)

def register_shape(self, name, shape=None):
    if shape is None:
        # 形状名称中需要加入"."才能用于图片
        if "." in name:
            shape = Shape("image", self._image(name))
        else:
            raise TurtleGraphicsError("Bad arguments for register_shape.\n"
                                      + "Use  help(register_shape)" )
    elif isinstance(shape, tuple):
        shape = Shape("polygon", shape)
    ## else shape assumed to be Shape-instance
    self._shapes[name] = shape

def _drawturtle(self):
    """Manages the correct rendering of the turtle with respect to
    its shape, resizemode, stretch and tilt etc."""
    screen = self.screen
    shape = screen._shapes[self.turtle.shapeIndex]
    ttype = shape._type
    titem = self.turtle._item
    if self._shown and screen._updatecounter == 0 and screen._tracing > 0:
        self._hidden_from_screen = False
        tshape = shape._data
        if ttype == "polygon":
            if self._resizemode == "noresize": w = 1
            elif self._resizemode == "auto": w = self._pensize
            else: w =self._outlinewidth
            shape = self._polytrafo(self._getshapepoly(tshape))
            fc, oc = self._fillcolor, self._pencolor
            screen._drawpoly(titem, shape, fill=fc, outline=oc,
                                                  width=w, top=True)
        elif ttype == "image":
            screen._drawimage(titem, self._position, tshape,
                              self.heading(),self._stretchfactor[0])
        elif ttype == "compound":
            for item, (poly, fc, oc) in zip(titem, tshape):
                poly = self._polytrafo(self._getshapepoly(poly, True))
                screen._drawpoly(item, poly, fill=self._cc(fc),
                                 outline=self._cc(oc), width=self._outlinewidth, top=True)
    else:
        if self._hidden_from_screen:
            return
        if ttype == "polygon":
            screen._drawpoly(titem, ((0, 0), (0, 0), (0, 0)), "", "")
        elif ttype == "image":
            screen._drawimage(titem, self._position,
                                      screen._shapes["blank"]._data)
            if titem in images:del images[titem] # 如果已隐藏，则释放图像引用
        elif ttype == "compound":
            for item in titem:
                screen._drawpoly(item, ((0, 0), (0, 0), (0, 0)), "", "")
        self._hidden_from_screen = True

def _drawline(self, lineitem, coordlist=None,
              fill=None, width=None, top=False):
    """Configure lineitem according to provided arguments:
    coordlist is sequence of coordinates
    fill is drawing color
    width is width of drawn line.
    top is a boolean value, which specifies if polyitem
    will be put on top of the canvas' displaylist so it
    will not be covered by other items.
    """
    if coordlist is not None:
        cl=(value for coord in coordlist for value in 
            (coord[0] * self.xscale, -coord[1] * self.yscale)) # 迭代器
        self.cv.coords(lineitem, *cl)
    if fill is not None:
        self.cv.itemconfigure(lineitem, fill=fill)
    if width is not None:
        self.cv.itemconfigure(lineitem, width=width)
    if top:
        self.cv.tag_raise(lineitem)

def _goto(self, end): # 优化绘制较长天体轨道的性能
    """Move the pen to the point end, thereby drawing a line
    if pen is down. All other methods for turtle movement depend
    on this one.
    """
    ## Version with undo-stuff
    go_modes = ( self._drawing,
                 self._pencolor,
                 self._pensize,
                 isinstance(self._fillpath, list))
    screen = self.screen
    undo_entry = ("go", self._position, end, go_modes,
                  (self.currentLineItem,
                  self.currentLine[:],
                  screen._pointlist(self.currentLineItem),
                  self.items[:])
                  )
    if self.undobuffer:
        self.undobuffer.push(undo_entry)
    start = self._position
    if self._speed and screen._tracing == 1:
        diff = (end-start)
        diffsq = (diff[0]*screen.xscale)**2 + (diff[1]*screen.yscale)**2
        nhops = 1+int((diffsq**0.5)/(3*(1.1**self._speed)*self._speed))
        delta = diff * (1.0/nhops)
        for n in range(1, nhops):
            if n == 1:
                top = True
            else:
                top = False
            self._position = start + delta * n
            if self._drawing:
                screen._drawline(self.drawingLineItem,
                                 (start, self._position),
                                 self._pencolor, self._pensize, top)
            self._update()
        if self._drawing:
            screen._drawline(self.drawingLineItem, ((0, 0), (0, 0)),
                                           fill="", width=self._pensize)
    # Turtle now at end,
    if self._drawing: # now update currentLine
        self.currentLine.append(end)
    if isinstance(self._fillpath, list):
        self._fillpath.append(end)
    ######    vererbung!!!!!!!!!!!!!!!!!!!!!!
    self._position = end
    if self._creatingPoly:
        self._poly.append(end)
    if len(self.currentLine) > 320: # tkinter.Canvas上一条线的最大长度，turtle中原本为42
        self._newLine()
    self._update() #count=True)

if Image: # 若导入PIL模块成功
    # 用重写的函数替换turtle模块中原来的函数
    turtle.TurtleScreenBase._image=_image
    turtle.TurtleScreenBase._createimage=_createimage
    turtle.TurtleScreenBase._drawimage=_drawimage
    turtle.TurtleScreen.register_shape=register_shape
    turtle.RawTurtle._drawturtle=_drawturtle

# 不依赖PIL
turtle.TurtleScreenBase._drawline=_drawline
turtle.RawTurtle._goto=_goto

# ---------------------重写结束-------------------------

class GravSys(solar_system.GravSys):
    # 引力系统
    __slots__=solar_system.GravSys.__slots__+["dt_s"]
    def __init__(self,scr=None):
        super().__init__(scr)
        self.dt = 0.0005 # 速度
        self.dt_s=0.000005
        #speed: 程序在绘制一帧之前执行计算的次数
        self.speed=8
    def increase_speed(self,event=None):
        self.dt_s*=1.1
    def decrease_speed(self,event=None):
        self.dt_s/=1.1
    _onrelease=_copy_func(solar_system.GravSys._onrelease,globals()) # 使用本模块中的SpaceCraft类

l=[]
class Star(solar_system.Star):
    def step(self):
        # 计算行星位置
        dt = self.gs.dt
        self.dx += dt*self.ax
        self.dy += dt*self.ay

        self.x+= dt*self.dx
        self.y+= dt*self.dy

        speed=0.9
        self.dx*=pow(speed,dt)
        self.dy*=pow(speed,dt)
        d=self.distance(self.sun)
        l.append(d)
        if d<=0.62:
            print('Dropped')
        self.gs.dt=d**(3/2)*self.gs.dt_s

class RoundStar(solar_system.RoundStar,Star):
    pass

class Sun(solar_system.Sun,Star):
    pass

class SpaceCraft(solar_system.SpaceCraft,Star):
    pass

IMAGE="BlackHole.jpg"
def main():
    scr=Screen()
    scr.screensize(6000,6000)
    try:
        scr._canvas.master.state("zoomed")
    except TclError:pass
    scr.bgcolor("black")
    scr.tracer(0,0)
    scr.register_shape(IMAGE)

    gs = GravSys(scr)
    sun = Sun(gs,"太阳",SUN_MASS, (0,0), (0,0),
              1,has_orbit=False,shape=(IMAGE,"yellow"),rotation = 360)

    # 地球
    earth = Star(gs,"地球",EARTH_MASS, (260,0), (0,173),
                 2.1, shape=("blue","blue4"))

    # 绑定键盘事件
    cv=scr.getcanvas()
    cv.bind_all("<Key-Up>",gs.up)
    cv.bind_all("<Key-Down>",gs.down)
    cv.bind_all("<Key-Left>",gs.left)
    cv.bind_all("<Key-Right>",gs.right)
    cv.bind_all("<Key-equal>",gs.increase_speed)
    cv.bind_all("<Key-minus>",gs.decrease_speed)
    cv.master.bind("<Key-Tab>",gs.switch) # 修复python 3.10+下无法绑定的bug
    cv.bind_all("<Key-Delete>",gs.del_planet)
    cv.master.bind("<Shift-Key-Tab>",gs.reverse_switch)
    cv.bind_all("<Control-Key-equal>",lambda event:gs.zoom(4/3.0)) #Ctrl+"+"
    cv.bind_all("<Control-Key-minus>",lambda event:gs.zoom(3/4.0)) #Ctrl+"-"
    cv.bind_all("<Control-Key-d>",gs.clear_spacecrafts)
    cv.bind("<Button-1>",gs._onclick)
    cv.bind("<B1-Motion>",gs._ondrag)
    cv.bind("<B1-ButtonRelease>",gs._onrelease)

    globals().update(locals()) # 便于程序退出后, 在交互模式(>>> )中调试程序
    gs.init()
    try:gs.start()
    except (Terminator,TclError):pass

if __name__ == '__main__':
    main()
    if scr._RUNNING:mainloop()
