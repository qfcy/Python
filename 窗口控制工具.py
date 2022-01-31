from ctypes import *
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.simpledialog import askstring
import time

__version__ = '1.1.03'
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
hwnd=0;_top=False;old=(WS_VISIBLE,0)

def top():
    global _top
    if not _top:
        windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 3) # 窗口置顶
    else:
        windll.user32.SetWindowPos(hwnd, -2, 0, 0, 0, 0, 3)
    _top = not _top

def minimize(): # 最小化
    windll.user32.CloseWindow(hwnd)
def unminimize():# 取消最小化
    windll.user32.OpenIcon(hwnd)
def close(): # 关闭窗口
    windll.user32.SendMessageA(hwnd,WM_CLOSE,0,0)

def settitle(): # 设置标题
    title=askstring('','输入窗口标题')
    windll.user32.SetWindowTextW(hwnd, title)

def reset_style():
    global old
    old = (windll.user32.GetWindowLongA(hwnd,GWL_STYLE),
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

    def normal():
        windll.user32.SetWindowLongA(hwnd, GWL_STYLE, old[0])
        windll.user32.SetWindowLongA(hwnd, GWL_EXSTYLE, old[1])
    _addoption(win,'正常',normal)
    # 设置GWL_STYLE时须加入WS_VISIBLE+WS_CLIPSIBLINGS+WS_CLIPCHILDREN,使窗口可用
    _addoption(win,'无边框',
               lambda:windll.user32.SetWindowLongA(hwnd, GWL_STYLE,
                                WS_VISIBLE+WS_CLIPSIBLINGS+WS_CLIPCHILDREN))
    _addoption(win,'细边框',
               lambda:windll.user32.SetWindowLongA(hwnd, GWL_STYLE,
                    WS_VISIBLE+WS_CLIPSIBLINGS+WS_CLIPCHILDREN + WS_THICKFRAME))
    _addoption(win,'边框加粗',
               lambda:windll.user32.SetWindowLongA(hwnd,
                                            GWL_EXSTYLE, WS_EX_CLIENTEDGE))
    _addoption(win,'允许文件拖入',
        lambda:windll.user32.SetWindowLongA(hwnd,
                                            GWL_EXSTYLE, WS_EX_ACCEPTFILES))
    _addoption(win,'工具窗口',
        lambda:windll.user32.SetWindowLongA(hwnd,GWL_EXSTYLE, WS_EX_TOOLWINDOW))

    ttk._Button(win,text='取消',command=win.destroy).pack(side=tk.RIGHT)
    ttk._Button(win,text='确定',command=confirm).pack(side=tk.RIGHT)
    win.grab_set();win.focus_force()


def findwin(*args):
    global hwnd,_top
    hwnd=windll.user32.FindWindowW(c_char_p(None),winname.get())
    print(hwnd)
    _setbtn()
    _top=False
    reset_style()

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
    if prev2 != hwnd:reset_style()
    _setbtn()

def select_win():
    window=tk.Tk()
    window["bg"]="white";window["cursor"]="target"
    window.title("请选择窗口")
    window.attributes("-alpha",0.2)
    window.attributes("-topmost",True)
    window.attributes("-fullscreen",True)
    window.bind('<Button-1>',_getwin)

root=tk.Tk()
root.title('窗口控制工具')
tk.Label(root,text='输入窗口名').pack()
winname=tk.StringVar()
__callback_name = winname.trace('w',findwin)
ttk.Entry(root,textvariable=winname).pack(fill=tk.X,padx = 10)

frame=tk.Frame(root)
ttk._Button(frame,text='选择窗口',command=select_win).grid(row=1,column=1)
ttk.Button(frame,text='置顶/取消置顶',command=top,
           state=tk.DISABLED).grid(row=1,column=2)
ttk.Button(frame,text='最小化',command=minimize,
           state=tk.DISABLED).grid(row=2,column=1)
ttk.Button(frame,text='取消最小化',command=unminimize,
           state=tk.DISABLED).grid(row=2,column=2)
ttk.Button(frame,text='关闭',command=close,
           state=tk.DISABLED).grid(row=3,column=1)
ttk.Button(frame,text='更改标题',command=settitle,
           state=tk.DISABLED).grid(row=3,column=2)
ttk.Button(frame,text='更改样式',command=set_style,
           state=tk.DISABLED).grid(row=4,column=1)

frame.pack()
root.mainloop()
