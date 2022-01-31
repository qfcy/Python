import tkinter,os,timer
from tkinter import *
import tkinter.ttk as ttk

def click():
    global x
    if x % 3==0:
        ttk.Button(text="按钮"+str(x),command=click).pack()#按钮每单击一次,就新建一个按钮
    else:
        ttk.Button(text="按钮"+str(x),command=click).pack()
    x+=1

t=timer.Timer()
window=tkinter.Tk() #创建一个窗口
window.title("GUI程序")
app_path=os.path.split(os.path.realpath(__file__))[0]#获取程序路径
try:
    window.iconbitmap(app_path+"/图标/窗口.ico")#加载图标
except:pass
tkinter.Button(text="+ 添加按钮",command=click).pack()
x=1
#使窗口缓慢弹出
window.iconify()
window.update()
window.deiconify()
t.printtime() #输出程序用时

mainloop()