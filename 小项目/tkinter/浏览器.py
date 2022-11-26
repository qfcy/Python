from urllib.request import urlopen
import sys,re
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.scrolledtext import ScrolledText
import tkinter.messagebox as msgbox

_title="Web浏览器"
_ignore_chars=["{","}","(",")","#","font","var","++","--"]

def ignore_html(code):
    return re.sub("(<.*?>|&nbsp;)","",code)
def clear_emptylines(text):
    return text.replace("\r\n\r\n",'\n')
def iscode(text):
    if text.endswith(';') or ('=' in text and ';' in text):return True
    for char in _ignore_chars:
        if char in text:return True
    return False
def ignore_js(text):
    lines=text.splitlines()
    try:
       i=0
       while True:
            if iscode(lines[i]):del lines[i]
            else:i+=1
    except IndexError:pass
    return '\n'.join(lines)

class Browser():
    _encodings="ansi","utf-8","utf-16","utf-32","gbk","big5"
    _normalurl="https://baike.baidu.com"
    def __init__(self,master):
        self.master=master
        self.master.bind("<Key>",self.onkey)
        self.urls=[self._normalurl]

        self.textbox=ScrolledText()
        self.textbox.pack(side=tk.BOTTOM,expand=True,fill=tk.BOTH)
        self.options=tk.Frame()
        self.options.pack(side=tk.BOTTOM,fill=tk.X)
        self.create_options(self.options)
        self.url=tk.StringVar()
        self.urlbox=ttk.Combobox(master,textvariable=self.url)
        self.urlbox["value"]=self.urls
        self.urlbox.pack(side=tk.LEFT,expand=True,fill=tk.X)
        self.urlbox.bind("<Key>",self.onkey)
        self.urlbox.focus_force()
        self.browsebutton=ttk.Button(master,text="访问网址",command=self.load)
        self.browsebutton.pack(side=tk.RIGHT)
        self.create_menu()
    def create_options(self,master):
        tk.Label(master,text="忽略:").pack(side=tk.LEFT)
        self.is_ightml=tk.IntVar();self.is_ightml.set(1)
        self.is_igjs=tk.IntVar();self.is_igjs.set(1)
        tk.Checkbutton(master,text="HTML(XML)代码",variable=self.is_ightml)\
        .pack(side=tk.LEFT)
        tk.Checkbutton(master,text="JavaScript",variable=self.is_igjs)\
        .pack(side=tk.LEFT)
        
        tk.Label(master,text="编码:").pack(side=tk.LEFT)
        self.coding=tk.StringVar()
        self.coding.set("utf-8")
        coding=ttk.Combobox(master,textvariable=self.coding)
        coding["value"]=self._encodings
        coding.pack(side=tk.LEFT)
    def create_menu(self):
        menu=tk.Menu(self.textbox,tearoff=False)
        menu.add_command(label="复制 ",accelerator="Ctrl+C",
                         command=lambda:self.textbox.event_generate("<<Copy>>"))
        self.textbox.bind("<Button-3>",
                    lambda event:menu.post(event.x_root,event.y_root))
        
        menu2=tk.Menu(self.urlbox,tearoff=False)
        menu2.add_command(label="复制",accelerator="Ctrl+C",
                         command=lambda:self.urlbox.event_generate("<<Copy>>"))
        menu2.add_command(label="粘贴并访问",command=lambda:self.urlbox.event_generate("<<Paste>>")==self.load())
        self.urlbox.bind("<Button-3>",
                    lambda event:menu2.post(event.x_root,event.y_root))
    def onkey(self,event):
        if event.char=='\r':self.load()
    def load(self,url=None):
        if not url:
            url=self.url.get()
            if not url:return
        else:self.url.set(url)
        try:
            self.master.title("加载中")
            self.master.update()
            if not url.startswith("http") and not url.startswith("ftp"):
                url="file:"+url
            webpage=urlopen(url)
            text=str(webpage.read(),encoding=self.coding.get(),errors="replace")
            #清除文本中的代码和空行
            if self.is_ightml.get():text=ignore_html(text)
            if self.is_igjs.get():text=ignore_js(text)
            self.textbox.delete("1.0",tk.END)
            self.textbox.insert(tk.INSERT,text)
            self.master.title(_title+" - "+url)
            #self.textbox.focus_force()
            if url not in self.urls:
                self.urls.append(url)
                self.urlbox["value"]=self.urls
        except Exception as err:
            self.master.title(_title)
            msgbox.showinfo(type(err).__name__,
                            "抱歉,无法打开该网页或文件{}"
                            .format(':\n'+str(err) if str(err) else '。'))
            self.urlbox.focus_force()

def main():
    root=tk.Tk()
    root.title(_title)
    browser=Browser(root)
    if len(sys.argv)>1:browser.load(sys.argv[1])
    root.mainloop()

if __name__=="__main__":main()