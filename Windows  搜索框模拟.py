import os
from urllib.parse import quote
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.font import Font
from tk_dragtool import draggable
import tkinter.messagebox as msgbox
import windnd

path=None
def ondrag(filenames):
    print(filenames)
    global path
    if len(filenames)!=1 or not \
       os.path.isdir(filenames[0].decode("ansi")):
        msgbox.showinfo("","只允许拖曳一个文件夹")
    path = filenames[0].decode("ansi")
    tip["text"]="当前搜索范围: "+path

def launch_search():
    if path is None:
        msgbox.showinfo("","您还没有选择搜索范围!")
    word = kw.get()
    title = path # bug:路径为中文时有乱码
    url = 'search-ms:displayname=%s&crumb=&crumb=System.Generic.String:%s&crumb=location:%s'%(
        quote(title), quote(word), quote(path))
    print(url)
    # cmd命令中, ^将&符号转义
    os.system('start '+url.replace('&','^&'))

root=tk.Tk()
root.title("Windows 搜索框模拟")
root.geometry("400x60")
#root.overrideredirect(True) 去除窗口的边框
f=Font(root,size=20)
tip=tk.Label(root,text="拖曳搜索范围的文件夹到此: ")
tip.pack(side=tk.TOP,fill=tk.X)
kw=ttk.Entry(root,font=("Microsoft Yahei",12,"normal"))
kw.pack(side=tk.LEFT,expand=True,fill=tk.BOTH)
btn=ttk.Button(root,text="搜索",command=launch_search,width=6)
btn.pack(side=tk.RIGHT,fill=tk.Y)
windnd.hook_dropfiles(root,func=ondrag)
root.mainloop()