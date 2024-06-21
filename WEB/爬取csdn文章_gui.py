from requests import get
import re,_thread,os
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as msgbox
from tkinter.scrolledtext import ScrolledText

PATH = "." #"save"
def log(text): # 添加日志
    lock.acquire()
    log_text.insert(tk.END,text)
    lock.release()
def fetch(url,path):
    headers = {
    "User-Agent": """Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 \
    (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"""
    }
    log("保存中 ...\n")
    try:
        req = get(url,headers=headers)
        if req.status_code!=200:
            raise Exception("Invalid status code %d"%req.status_code)
        text=req.content.decode('utf-8')
        patt=re.compile('<article.*</article>',re.S)
        #css_patt=re.compile('<link rel="stylesheet" href=".*?blog.*?"',re.S)

        title=re.findall('<title>(.*?)</title>',text,re.S)[0]
        content='''<html><head><meta charset="utf-8">\
        <title>%s</title><body>'''%title
        #for css in re.findall(css_patt,text):
        #    content+=css+'>'

        content += re.findall(patt,text)[0]
        content += '</body></html>'

        # 去除文件名不能包含的特殊字符
        tbl = str.maketrans('','','\\/:*?"<>|')
        filename = '%s.html'%title.translate(tbl)
        filepath = os.path.join(path,filename)
        with open(filepath,'w',encoding='utf-8') as f:
            f.write(content)
    except Exception as err:
        log("保存失败, %s: %s\n\n" % (type(err).__name__,str(err)))
    else:
        log("%s 保存成功\n\n" % filename)

def ok_click(event=None):
    _thread.start_new_thread(fetch,(url_input.get(),PATH))

lock=_thread.allocate_lock()

win=tk.Tk()
win.geometry("360x300")
win.title("CSDN文章爬取、保存小工具")

tk.Label(win,text="输入文章网址(URL):").pack(side=tk.TOP)

inputbox=tk.Frame(win)
url_input=ttk.Entry(inputbox)
url_input.pack(side=tk.LEFT,expand=True,fill=tk.X)
url_input.bind("<Key-Return>",ok_click)

ttk.Button(inputbox,text="保存",command=ok_click,width=10).pack(side=tk.LEFT)
inputbox.pack(side=tk.TOP,fill=tk.X)

log_text=ScrolledText(win,wrap=tk.CHAR)
log_text.insert(tk.END,"日志记录\n\n")
log_text.pack(side=tk.TOP,expand=True,fill=tk.BOTH)

win.mainloop()