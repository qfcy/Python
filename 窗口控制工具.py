from ctypes import *
from ctypes import wintypes
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.simpledialog import askstring
import time

__version__ = '1.1.1'

class Rect(Structure):
    _fields_ = [("left", wintypes.LONG),
                ("top", wintypes.LONG),
                ("right", wintypes.LONG),
                ("bottom", wintypes.LONG)]

# 以下代码用于管理按钮
ttk._Button=ttk.Button
buttons=[]
def Button(*args,**kw):
    b=ttk._Button(*args,**kw)
    buttons.append(b)
    return b
def _setbtn():
    if hwnd != 0:
        for b in buttons:b['state']=tk.NORMAL
    else:
        for b in buttons:b['state']=tk.DISABLED
ttk.Button=Button;del Button

WM_CLOSE = 0x10
WM_SETTEXT = 0x0c
GWL_STYLE = -16
GWL_EXSTYLE = -20
SW_MINIMIZE = 6
SW_MAXIMIZE = 3
SW_RESTORE = 9
SW_HIDE = 0

WS_BORDER = 0x800000
WS_CAPTION = 0xC00000 # WS_BORDER Or WS_DLGFRAME
WS_CHILD = 0x40000000
WS_CLIPCHILDREN = 0x2000000
WS_CLIPSIBLINGS = 0x4000000
WS_POPUP = 0x80000000
WS_DLGFRAME = 0x400000
WS_DISABLED = 0x8000000
WS_OVERLAPPEDWINDOW = 0xcf0000
WS_THICKFRAME = 0x40000
WS_VISIBLE = 0x10000000

WS_EX_APPWINDOW = 0x40000
WS_EX_DLGMODALFRAME = 0x1
WS_EX_ACCEPTFILES = 0x10
WS_EX_CLIENTEDGE= 0x200
WS_EX_TOOLWINDOW = 0x80
WS_EX_WINDOWEDGE = 0x100

LWA_ALPHA = 0x2;LWA_COLORKEY=0x1
WS_EX_LAYERED = 0x80000
hwnd=0;_top=False;_fullscreen=False
old_style=(WS_VISIBLE,0)
rect=Rect()

def top():
    global _top
    if not _top:
        windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 3) # 窗口置顶
    else:
        windll.user32.SetWindowPos(hwnd, -2, 0, 0, 0, 0, 3)
    _top = not _top

def minimize(): # 最小化
    windll.user32.ShowWindow(hwnd,SW_MINIMIZE)# 也可用windll.user32.CloseWindow(hwnd)
def maximize():# 最大化
    windll.user32.ShowWindow(hwnd,SW_MAXIMIZE)
    time.sleep(0.1)
    root.focus_force()
def restore():# 还原
    windll.user32.ShowWindow(hwnd,SW_RESTORE)
    time.sleep(0.1)
    root.focus_force()
def close(): # 关闭窗口
    windll.user32.SendMessageA(hwnd,WM_CLOSE,0,0)

def settitle(): # 设置标题
    title=askstring('','输入窗口标题')
    windll.user32.SetWindowTextW(hwnd, title)

def backup_attributes(): # 备份原先的窗口属性
    global old_style,rect
    rect = Rect()
    windll.user32.GetWindowRect(hwnd, byref(rect))
    old_style = (windll.user32.GetWindowLongA(hwnd,GWL_STYLE),
           windll.user32.GetWindowLongA(hwnd,GWL_EXSTYLE))

def set_style():# 设置窗口样式
    win=tk.Toplevel(root)
    win.title('更改样式')
    count = 0;funcs=[];v=tk.IntVar(win)
    def _addoption(master,text,command): # 用于管理选项按钮
        nonlocal count
        funcs.append(command)
        butt = ttk.Radiobutton(master,text=text,variable=v,value=count)
        butt.pack(side=tk.TOP)
        count += 1
    def confirm():
        funcs[v.get()]()
        win.destroy()

    def default():
        windll.user32.SetWindowLongA(hwnd, GWL_STYLE, old_style[0])
        windll.user32.SetWindowLongA(hwnd, GWL_EXSTYLE, old_style[1])
    _addoption(win,'默认样式',default)
    # 设置GWL_STYLE时须加入WS_VISIBLE+WS_CLIPSIBLINGS+WS_CLIPCHILDREN,使窗口可用
    _addoption(win,'无边框',
               lambda:windll.user32.SetWindowLongA(hwnd, GWL_STYLE,
               old_style[0] & (~WS_BORDER)))
    _addoption(win,'细边框',
               lambda:windll.user32.SetWindowLongA(hwnd, GWL_STYLE,
               old_style[0] | WS_THICKFRAME | WS_BORDER))
    _addoption(win,'边框加粗',
               lambda:windll.user32.SetWindowLongA(hwnd,
                                            GWL_EXSTYLE, old_style[1] | WS_EX_CLIENTEDGE))
    _addoption(win,'允许文件拖入',
        lambda:windll.user32.SetWindowLongA(hwnd,
                                            GWL_EXSTYLE, old_style[1] | WS_EX_ACCEPTFILES))
    _addoption(win,'工具窗口',
        lambda:windll.user32.SetWindowLongA(hwnd,GWL_EXSTYLE,old_style[1] | WS_EX_TOOLWINDOW))

    ttk._Button(win,text='取消',command=win.destroy).pack(side=tk.RIGHT)
    ttk._Button(win,text='确定',command=confirm).pack(side=tk.RIGHT)
    win.grab_set();win.focus_force()

def set_alpha():# 设置窗口透明度
    def confirm():
        exstyle = windll.user32.GetWindowLongA(hwnd, GWL_EXSTYLE)
        exstyle |= WS_EX_LAYERED  # 使窗口具有能设置透明度的样式
        windll.user32.SetWindowLongA(hwnd, GWL_EXSTYLE, exstyle)
        # 设置透明度
        windll.user32.SetLayeredWindowAttributes(hwnd,0,
                                                 int(alpha.get()),LWA_ALPHA)
        win.destroy()

    win=tk.Toplevel(root)
    win.title('更改透明度')
    alpha=ttk.Scale(win,from_=0,to=255,length=200,
                    orient=tk.HORIZONTAL)
    alpha.set(192);alpha.pack()
    ttk._Button(win,text='取消',command=win.destroy).pack(side=tk.RIGHT)
    ttk._Button(win,text='确定',command=confirm).pack(side=tk.RIGHT)

def fullscreen(): # 全屏
    global _fullscreen
    if not _fullscreen:
        windll.user32.SetWindowLongA(hwnd, GWL_STYLE, old_style[0] & (~WS_BORDER))
        #windll.user32.MoveWindow(hwnd, 0, 0, root.winfo_screenwidth(),
        #                         root.winfo_screenheight(),True)
        windll.user32.ShowWindow(hwnd, SW_MAXIMIZE)
    else:
        windll.user32.SetWindowLongA(hwnd, GWL_STYLE, old_style[0])
        windll.user32.MoveWindow(hwnd, rect.left, rect.top, rect.right-rect.left,
                                 rect.bottom-rect.top, True)
        windll.user32.ShowWindow(hwnd, SW_RESTORE)
    _fullscreen = not _fullscreen

def hide(): # 隐藏窗口
    windll.user32.ShowWindow(hwnd,SW_HIDE)

def findwin(*args):
    global hwnd,_top
    hwnd=windll.user32.FindWindowW(c_char_p(None),winname.get())
    #print(hwnd)
    _setbtn()
    _top=False
    backup_attributes()

class PointAPI(Structure):
    #PointAPI类型,用于获取鼠标坐标
    _fields_ = [("x", c_ulong), ("y", c_ulong)]

def _getwin(event):
    # 用于根据鼠标位置选择窗口
    global hwnd
    po = PointAPI()
    windll.user32.GetCursorPos(byref(po))
    event.widget.destroy()

    prev2=hwnd
    prev= hwnd = windll.user32.WindowFromPoint(po.x,po.y) # 获取句柄
    p = create_string_buffer(256)
    windll.user32.GetWindowTextW(hwnd,byref(p),256) # 获取窗口标题
    title = str(p.raw,encoding='utf-16').strip('\x00')

    winname.trace_remove('write',__callback_name) # 避免调用set方法时修改了hwnd
    winname.set(title)
    winname.trace('w',findwin)
    if prev2 != hwnd:backup_attributes()
    _setbtn()

def select_win():
    window=tk.Tk()
    window["bg"]="white";window["cursor"]="target"
    window.title("请选择窗口")
    window.attributes("-alpha",0.2)
    window.attributes("-topmost",True)
    window.attributes("-fullscreen",True)
    window.bind('<B1-ButtonRelease>',_getwin)

root=tk.Tk()
root.title('窗口控制工具')
root.geometry("300x260")
root.wm_attributes("-alpha",0.9) # 创建透明效果
tk.Label(root,text='输入窗口名或点击"选择窗口"').pack()
winname=tk.StringVar()
__callback_name = winname.trace('w',findwin)
ttk.Entry(root,textvariable=winname).pack(fill=tk.X,padx = 10)

frame=tk.Frame(root)
ttk._Button(frame,text='选择窗口',command=select_win).grid(row=1,column=1)
ttk.Button(frame,text='置顶/取消置顶',command=top,
           state=tk.DISABLED).grid(row=1,column=2)
ttk.Button(frame,text='最小化',command=minimize,
           state=tk.DISABLED).grid(row=2,column=1)
ttk.Button(frame,text='最大化',command=maximize,
           state=tk.DISABLED).grid(row=2,column=2)
ttk.Button(frame,text='还原',command=restore,
           state=tk.DISABLED).grid(row=3,column=1)
ttk.Button(frame,text='关闭',command=close,
           state=tk.DISABLED).grid(row=3,column=2)
ttk.Button(frame,text='更改标题',command=settitle,
           state=tk.DISABLED).grid(row=4,column=1)
ttk.Button(frame,text='更改样式',command=set_style,
           state=tk.DISABLED).grid(row=4,column=2)
ttk.Button(frame,text='更改透明度',command=set_alpha,
           state=tk.DISABLED).grid(row=5,column=1)
ttk.Button(frame,text='全屏/退出全屏',command=fullscreen,
           state=tk.DISABLED).grid(row=5,column=2)
ttk.Button(frame,text='隐藏',command=hide,
           state=tk.DISABLED).grid(row=6,column=1)
frame.pack()
root.mainloop()
