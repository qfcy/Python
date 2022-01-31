"""A number guessing game made by tkinter. Have FUN!
使用tkinter制作的猜数游戏。"""
import tkinter,os,time
from tkinter import *
import tkinter.ttk as ttk
from tkinter import messagebox as msgbox
from random import random

__email__="3416445406@qq.com"
__author__="七分诚意 qq:3076711200 邮箱:%s"%__email__
__version__="1.0.1"

def text_change():
    OK["state"]=NORMAL if txt.get().strip() else DISABLED

def btn(event=None):
    global n,caidui,cishu
    if caidui:reset()#判断是否已猜对 
    else:
        s=txt.get()
        if not s:return
        
        if int(s)==n:
            f['text']="猜对了,您真聪明!"
            OK['text']="再来一次"
            OK['width']=8
            caidui=True
        else:    #如果猜错了
            if cishu<=0:
                msgbox.showinfo("提示","您的次数已用完,下次再来吧。\n正确答案:"+str(n))
                quit()
            else:c['text']="您剩余的次数:"+str(cishu)
            if int(s) < n: #如果输入的数小了
                if int(s) + 10 > n:
                    if int(s) + 3 > n:
                        f['text'] = "小了一点点！"
                    else:
                        f['text'] = "小了一点,请再猜！"
                else:
                    f['text'] = "你猜得太小了，请再猜！"
            else:   #如果输入的数大了
                if int(s) - 10 > n:
                    f['text'] = "你猜得太大了，请再猜！"
                else:
                    if int(s) - 3 > n:
                        f['text'] = "大了一点,请再猜！"
                    else:
                        f['text'] = "大了一点点！"
            txt.focus_force()
        cishu-=1

def reset():#重置
    global n,caidui,cishu
    n=int(random()*100+1)#生成一个随机数
    f['text']=""#重设控件属性
    f['width']=5
    OK['text']="确定"
    caidui=False
    cishu=7
    c['text']="您剩余的次数:"+str(cishu)

if __name__=="__main__":
    window=Tk() #创建一个窗口
    window.title("猜数游戏")
    window.geometry('250x108')
    try:
        app_path=os.path.split(os.path.realpath(__file__))[0]#获取程序路径
        window.iconbitmap(app_path+r"\图标\数字.ico")#加载窗口图标
    except:pass#错误处理

    Label(text="有一个100内的整数给你猜",font="楷体").pack(fill=X)
    inputbox=Frame(window)
    OK=ttk.Button(inputbox,width=5,command=btn,state=DISABLED)
    OK.pack(side=RIGHT)
    txt=ttk.Entry(inputbox)
    txt.pack(side=LEFT,expand=True,fill=X)
    txt.bind("<Key>",lambda event:txt.after(50,text_change))
    txt.bind("<Key-Return>",btn)
    txt.focus_force()
    inputbox.pack(expand=True,fill=BOTH)
    c=Label(text="")
    c.pack(fill=X)
    f=Label(text="",font="隶书")
    f.pack(side=BOTTOM,fill=X)
    reset()

    mainloop()
