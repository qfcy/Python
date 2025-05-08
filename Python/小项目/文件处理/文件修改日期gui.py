import sys,os,time,traceback
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as msgbox
import windnd

def onfiledrag(filelist):
    filelist=[b.decode("ansi") for b in filelist] # 解码二进制的参数
    update_files(filelist)
def update_files(filelist):
    for file in filelist:
        if file not in files: # 避免重复
            files.append(file)
    file_tip["text"]="已拖入文件%d个:\n" % len(files) + \
                     "\n".join(files)


def get_today():
    t=time.localtime()
    return "%d %d %d %d %d"%(t.tm_year,t.tm_mon,t.tm_mday,t.tm_hour,t.tm_min)

def update_date(event=None): # event为可选参数
    if len(files)==0:
        msgbox.showinfo("提示","请拖入文件或文件夹!")
        return
    success=[];fail=[]
    raw_dt = date.get()
    d="";dt=""
    for s in raw_dt: # 去除标点字符
        if "0"<=s<="9":
            d+=s
        else:
            dt+=d+" "
            d=""
    dt+=d
    try:tm=time.mktime(time.strptime(dt, FORMAT))
    except Exception:
        msgbox.showinfo("提示","输入的日期格式错误")
        return
    for file in files:
        try:
            os.utime(file,(tm,tm))
            success.append(file)
        except Exception:
            #traceback.print_exc()  # 输出错误信息
            fail.append(file)
    msgbox.showinfo("修改完毕","修改成功：\n" + ("\n".join(success) if success else "无") +\
                    "\n修改失败：\n" + ("\n".join(fail) if fail else "无") )

def clear():
    files.clear() # 清空列表
    file_tip["text"]="向这里拖入文件或文件夹"

FORMAT = "%Y %m %d %H %M"
files=[]

win=tk.Tk()
win.geometry("350x300")
win.title("文件修改日期小工具")

tk.Label(win,text="输入新的修改日期 (年,月,日,时,分):").pack(side=tk.TOP)
inputbox=tk.Frame(win)

date=tk.StringVar()
date.set(get_today())
date_input=ttk.Entry(inputbox,textvariable=date)
date_input.pack(side=tk.LEFT,expand=True,fill=tk.X)
date_input.bind("<Key-Return>",update_date)

ttk.Button(inputbox,text="确定",command=update_date).pack(side=tk.LEFT)
ttk.Button(inputbox,text="清空",command=clear,width=5).pack(side=tk.LEFT)
inputbox.pack(side=tk.TOP)

# 如果拖入的是文件夹，那么只会更新文件夹本身的修改日期，而不是文件夹中所有文件的修改日期
file_tip=tk.Label(win,text="向这里拖入文件或文件夹")
file_tip.pack(side=tk.TOP)
windnd.hook_dropfiles(win,func=onfiledrag)

if len(sys.argv)>=2: # 处理命令行参数
    update_files(sys.argv[1:])
win.mainloop()