"""调用API函数,模拟鼠标移动和点击的模块。
示例:
#使用Aero Peek预览桌面。
from event import mouse
x,y=mouse.get_screensize()
mouse.move(x,y) #将鼠标移至屏幕右下角
mouse.click() #模拟鼠标点击
"""
import time
from ctypes import *

__all__=["get_screensize","getpos","goto","setpos",
         "move","click","right_click","dblclick"]

#API常量
MOUSEEVENTF_LEFTDOWN = 0x2
MOUSEEVENTF_LEFTUP = 0x4

MOUSEEVENTF_MIDDLEDOWN = 0x20
MOUSEEVENTF_MIDDLEUP = 0x40 

MOUSEEVENTF_RIGHTDOWN = 0x8
MOUSEEVENTF_RIGHTUP = 0x10 

MOUSEEVENTF_MOVE = 0x1
MOUSEEVENTF_WHEEL = 0x800
WHEEL_DELTA = 120

user32=windll.user32

class PointAPI(Structure):
    #PointAPI类型,用于获取鼠标坐标
    _fields_ = [("x", c_ulong), ("y", c_ulong)]

def get_screensize():
    "获取当前屏幕分辨率。"
    GetSystemMetrics = user32.GetSystemMetrics
    return GetSystemMetrics(0), GetSystemMetrics(1)

def getpos():
    """获取当前鼠标位置。
返回值为一个元组,以(x,y)形式表示。"""
    po = PointAPI()
    user32.GetCursorPos(byref(po))
    return int(po.x), int(po.y)

def goto(x,y):
    "将鼠标放在指定位置(x,y)。"
    user32.SetCursorPos(x,y)
setpos=goto

def move(x,y):
    """模拟移动鼠标。
与goto不同,move()*产生*一个鼠标事件。"""
    goto(x,y)
    user32.mouse_event(MOUSEEVENTF_MOVE,x,y,0,0)

def click(delay=0):
    "模拟鼠标左键单击"
    user32.mouse_event(MOUSEEVENTF_LEFTDOWN,0,0,0,0)
    time.sleep(delay)
    user32.mouse_event(MOUSEEVENTF_LEFTUP,0,0,0,0)

def right_click(delay=0):
    "模拟鼠标右键单击"
    user32.mouse_event(MOUSEEVENTF_RIGHTDOWN,0,0,0,0)
    time.sleep(delay)
    user32.mouse_event(MOUSEEVENTF_RIGHTUP,0,0,0,0)

def dblclick(delay=0.25):
    """模拟鼠标左键双击。
delay:双击的延时"""
    click()
    time.sleep(delay)
    click()

def dblclick2(delay=0.25):
    """模拟鼠标左键双击, 用户若在延时内移动鼠标, 双击仍会成功。
delay:双击的延时"""
    oldpos=getpos()
    click()
    time.sleep(delay)

    new=getpos()
    goto(*oldpos) # 防止用户移动鼠标使双击不成功
    click()
    goto(*new)

def middle_click(delay=0):
    "模拟单击鼠标中键"
    user32.mouse_event(MOUSEEVENTF_MIDDLEDOWN,0,0,0,0)
    time.sleep(delay)
    user32.mouse_event(MOUSEEVENTF_MIDDLEUP,0,0,0,0)

def leftdown():
    user32.mouse_event(MOUSEEVENTF_LEFTDOWN,0,0,0,0)
def leftup():
    user32.mouse_event(MOUSEEVENTF_LEFTUP,0,0,0,0)
def middledown():
    user32.mouse_event(MOUSEEVENTF_MIDDLEDOWN,0,0,0,0)
def middleup():
    user32.mouse_event(MOUSEEVENTF_MIDDLEUP,0,0,0,0)
def rightdown():
    user32.mouse_event(MOUSEEVENTF_RIGHTDOWN,0,0,0,0)
def rightup():
    user32.mouse_event(MOUSEEVENTF_RIGHTUP,0,0,0,0)

def wheel(delta):
    """模拟滚动鼠标滚轮。
delta: 滚动的距离, 正值为向上滚动, 负值为向下滚动。"""
    user32.mouse_event(MOUSEEVENTF_WHEEL,0,0,delta,0)