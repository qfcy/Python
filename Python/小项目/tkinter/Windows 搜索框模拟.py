# Windows 搜索框界面的模拟，用于替代Windows 10/11搜索框，
# 解决Windows 10/11搜索框不能打字或卡死的问题
import os
from urllib.parse import quote_from_bytes as _quote
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.font import Font
from tk_dragtool import bind_drag
import tkinter.messagebox as msgbox
import windnd

_safe = '''ABCDEFGHIJKLMNOPQRSTUVWXYZ\
abcdefghijklmnopqrstuvwxyz\
0123456789_.-~'''
# 重写quote方法, 使支持中文
# 已知: 系统不能识别已被quote的中文
def quote(string):
    result = ''
    for c in string:# _safe中的字符, 和非ASCII字符可以保留在url中
        if ord(c) < 128 and c not in _safe:
            result+=_quote(c.encode())
        else:
            result+=c
    return result

path=None
def ondrag(filenames):
    global path
    if len(filenames)!=1 or not \
       os.path.isdir(filenames[0].decode("ansi")):
        msgbox.showinfo("","只允许拖曳一个文件夹")
    path = filenames[0].decode("ansi")
    tip["text"]="当前搜索范围: "+path

def launch_search():
    if path is None:
        msgbox.showinfo("","您还没有选择搜索范围!")
        return
    word = kw.get()
    title = path
    url = 'search-ms:displayname=%s&crumb=&crumb=System.Generic.String:%s&crumb=location:%s'%(
        quote(title), quote(word), quote(path))
    print(url)
    # cmd命令中, ^将&符号转义
    os.system('start '+url.replace('&','^&'))

root=tk.Tk()
root.title("Windows 搜索框模拟")
root.geometry("400x60")
#root.overrideredirect(True) 去除窗口的边框
tip=tk.Label(root,text="拖曳搜索范围的文件夹到此: ")
tip.pack(side=tk.TOP,fill=tk.X)
bind_drag(root,tip) # 使用tk-dragtool库绑定拖曳

kw=ttk.Entry(root,font=("Microsoft Yahei",12,"normal"))
kw.pack(side=tk.LEFT,expand=True,fill=tk.BOTH)

btn=ttk.Button(root,text="搜索",command=launch_search,width=6)
btn.pack(side=tk.RIGHT,fill=tk.Y)

windnd.hook_dropfiles(root,func=ondrag) # 绑定文件夹拖入事件
root.mainloop()