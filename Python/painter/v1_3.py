import sys,os
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as dialog
import tkinter.messagebox as msgbox

_ver="1.3"
_title="画板 v"+_ver
_BACKCOLOR="white"
_STROKECOLOR="black"
_FILETYPE=("vec矢量图文件(*.vec)","*.vec")

class ScrolledCanvas(tk.Canvas):
    """Modeled after the scrolled canvas class from module turtle
    in the standard library.
    """
    def __init__(self,master,**options):
        self.frame=tk.Frame(master)
        tk.Canvas.__init__(self,self.frame,**options)
        
        self.hscroll=ttk.Scrollbar(self.frame,orient=tk.HORIZONTAL,
                                   command=self.xview)
        self.vscroll=ttk.Scrollbar(self.frame,command=self.yview)
        self.configure(xscrollcommand=self.hscroll.set,
                               yscrollcommand=self.vscroll.set)
        self._show_widgets()
        self.bind("<Configure>",self.adjustscrolls)
        self["scrollregion"]=(0,0,self["width"],self["height"])
    def _show_widgets(self,repack=False):
        if repack:self.pack_forget()
        self.vscroll.pack(side=tk.RIGHT,fill=tk.Y)
        self.hscroll.pack(side=tk.BOTTOM,fill=tk.X)
        self.pack(side=tk.BOTTOM,expand=True,fill=tk.BOTH)
    
    def adjustscrolls(self,event):
        region=self["scrollregion"].split()
        width,height=(int(region[2]),
                      int(region[3]))
        if event.width>width:
            self.hscroll.pack_forget()
        else:self._show_widgets(repack=True)
        if event.height>height:
            self.vscroll.pack_forget()
        else:self._show_widgets(repack=True)

class DictFile(dict):
    def __init__(self,filename=None,encoding="utf-8",error_callback=None,
                 toolarge_callback=None,max_size=100000):
        self.closed=False
        dict.__init__(self)
        self.filename=filename
        if not filename:return
        self.file=open(filename,encoding=encoding)
        lineno=0
        while True:
            try:
                texts=self.file.readline().split(":")
                if not texts[0]:break
                lineno+=1
                if len(texts)>1:
                    if len(texts[1])>max_size:
                        if callable(toolarge_callback):toolarge_callback(len(texts[1]))
                    self[texts[0]]=eval(texts[1],self)
            except Exception as err:
                if error_callback:error_callback(err,lineno)
        self.file.close()
    def __getattribute__(self,name):
        sp=super()
        if sp.__getattribute__("closed"):
            raise ValueError('invalid operation on closed DictFile object')
        else:return sp.__getattribute__(name)
    def save(self,writeall=False):
        self.file=open(self.filename,'w')
        for key in self.keys():
            if writeall or (not key.startswith("__")):
                self.file.write("{}:{}\n".format(key,repr(self[key])))
        self.file.close()
    def close(self):
        self.save()
        self.closed=True

class PropertyWindow(tk.Tk):
    instances=[]
    def __init__(self,master):
        self.init_window()
        self.master=master
        PropertyWindow.instances.append(self)
        
        self.create_widgets()
    def init_window(self):
        tk.Tk.__init__(self)
        self.title("文档属性")
        self.wm_attributes('-topmost',True)
        self.focus_force()

        self.bind("<Destroy>",
                  lambda event:PropertyWindow.instances.remove(self)
                  if self in PropertyWindow.instances else None)
    def create_widgets(self):
        size=tk.Frame(self)
        tk.Label(size,text="宽度(像素):").pack(side=tk.LEFT)
        self.width=tk.StringVar(self)
        self.width.set(self.master.data.get("width",
                                            self.master.cv.winfo_width()))
        ttk.Entry(size,textvariable=self.width,width=10).pack(side=tk.LEFT)
        tk.Label(size,text="高度(像素):").pack(side=tk.LEFT)
        self.height=tk.StringVar(self)
        self.height.set(self.master.data.get("height",
                                             self.master.cv.winfo_height()))
        ttk.Entry(size,textvariable=self.height,width=10).pack(side=tk.LEFT)
        size.pack(fill=tk.X)

        ttk.Separator(self).pack(fill=tk.X)
        backcolor=tk.Frame(self)
        tk.Label(backcolor,text="背景颜色:").pack(side=tk.LEFT)
        self.backcolor=tk.StringVar(self)
        self.backcolor.set(self.master.data.get("backcolor",''))
        tk.Entry(backcolor,textvariable=self.backcolor).pack(side=tk.LEFT)
        backcolor.pack(fill=tk.X)

        strokecolor=tk.Frame(self)
        tk.Label(strokecolor,text="画笔颜色:").pack(side=tk.LEFT)
        self.strokecolor=tk.StringVar(self)
        self.strokecolor.set(self.master.data.get("strokecolor",''))
        ttk.Entry(strokecolor,textvariable=self.strokecolor).pack(side=tk.LEFT)
        strokecolor.pack(fill=tk.X)

        buttons=tk.Frame(self)
        ttk.Button(buttons,text="确定",command=self.confirm).pack(side=tk.LEFT,padx=30)
        ttk.Button(buttons,text="取消",command=self.destroy).pack(
            side=tk.LEFT,padx=30)
        buttons.pack()
    def confirm(self):
        data=self.master.data
        data["width"]=self.width.get()
        data["height"]=self.height.get()
        data["backcolor"]=self.backcolor.get()
        data["strokecolor"]=self.strokecolor.get()
        self.master._clearcanvas()
        self.master.draw()
        self.master.file_changed=True
        self.destroy()

class Painter():
    instances=[]
    def __init__(self,master=None,filename=""):
        if master==None:
            self.master=tk.Tk()
            self.master.title(_title)
        else:self.master=master
        self.master.bind("<Key>",self.onkey)
        self.master.protocol("WM_DELETE_WINDOW",self.ask_for_save)
        for availble_path in sys.path:
            try:
                self.master.iconbitmap("%s\paint.ico"%availble_path)
            except tk.TclError:pass
        self.file_changed=False
        self.filename=filename
        Painter.instances.append(self)
        
        self.toolbar=tk.Frame(self.master,bg="gray92")
        self.toolbar.pack(side=tk.BOTTOM,fill=tk.X)
        self.create_toolbar(self.toolbar)
        self.create_canvas()
        self.create_menu()
        if self.filename:
            self.openfile(self.filename)
        else:
            self.data=DictFile()
            self.setdefault()
    def create_canvas(self):
        self.cv=ScrolledCanvas(self.master,bg="white",
                          cursor="pencil",relief=tk.GROOVE)
        self.cv.frame.pack(side=tk.BOTTOM,expand=True,fill=tk.BOTH)
        self.cv.bind("<Button-1>",self.mousedown)
        self.cv.bind("<B1-Motion>",self.paint)
        self.cv.bind("<B1-ButtonRelease>",self.mouseup)
        self.cv.bind("<Button-3>",
                     lambda event:self.menu.post(event.x_root,event.y_root))
    def create_menu(self):
        self.menu=tk.Menu(self.cv,tearoff=False)
        self.menu.add_command(label="撤销",command=lambda:self.undo(bell=True))
        self.menu.add_command(label="清除",command=self.clear)
        self.menu.add_separator()
        self.menu.add_command(label="文档属性",
                              command=self.show_property_window)
    def create_toolbar(self,master=None,buttonside=tk.BOTTOM):
        if not master:
            self.toolbar=master=tk.Frame()
            self.toolbar.pack(side=side,fill=tk.X)
        self.create_toolbutton(self.toolbar)
        self.toolbar_bind()
    def create_toolbutton(self,master):
        self.newbtn=ttk.Button(master,width=4,text="新建",command=self.new)
        self.newbtn.pack(side=tk.LEFT)
        self.openbtn=ttk.Button(master,width=4,text="打开",command=self.ask_for_open)
        self.openbtn.pack(side=tk.LEFT)
        self.savebtn=ttk.Button(master,width=4,text="保存",command=self.save)
        self.savebtn.pack(side=tk.LEFT)
        self.cleanbtn=ttk.Button(master,width=4,text="清除",command=self.clear)
        self.cleanbtn.pack(side=tk.LEFT)
        self.propertybtn=ttk.Button(master,width=8,text="文档属性",
                                    command=self.show_property_window)
        self.propertybtn.pack(side=tk.RIGHT)
    def toolbar_bind(self):
        self.toolbar.bind("<Button-1>",self.toolbar_mousedown)
        self.toolbar.bind("<B1-Motion>",self.move_toolbar)
        self.toolbar.bind("<B1-ButtonRelease>",self.toolbar_mouseup)
    def toolbar_mousedown(self,event):
        self.toolbar.config(bg="grey81",cursor="fleur")
    def move_toolbar(self,event):
        if event.y<-int(self.cv["height"]):#置于窗口上方
            self.cv.frame.forget();self.toolbar.forget()
            self.toolbar.pack(side=tk.TOP,fill=tk.X)
            self.cv.frame.pack(side=tk.TOP,expand=True,fill=tk.BOTH)
        elif event.y>int(self.cv["height"]):#置于窗口下方
            self.cv.frame.forget();self.toolbar.forget()
            self.toolbar.pack(side=tk.BOTTOM,fill=tk.X)
            self.cv.frame.pack(side=tk.BOTTOM,expand=True,fill=tk.BOTH)
        self.master.update()
    def toolbar_mouseup(self,event):
        self.toolbar.config(bg="gray92",cursor="arrow")
    def mousedown(self,event):
        data=self.data["data"]
        data.append([])#开始新的一根线
        data[-1].append((event.x,event.y))#将新绘制的点坐标附加在最近绘制的线末尾
    def paint(self,event):
        data=self.data["data"]
        try:
            x=data[-1][-1][0];y=data[-1][-1][1]
            self.cv.create_line(x,y,event.x,event.y,joinstyle=tk.ROUND,
                                capstyle=tk.ROUND,fill=self.data["strokecolor"])
            data[-1].append((event.x,event.y))
            self.file_changed=True
        except IndexError:pass
    def mouseup(self,event):
        try:
            if len(self.data["data"][-1])<=1:
                del self.data["data"][-1]
        except IndexError:pass
    def draw(self,data=None):
        if not data:data=self.data
        self.config_canvas(data)
        for line in data["data"]:
            args=[]
            for dot in line:
                args.extend([dot[0],dot[1]])
            self.cv.create_line(*args,joinstyle=tk.ROUND,
                                capstyle=tk.ROUND,fill=self.data["strokecolor"])
    def config_canvas(self,data=None):
        if not data:data=self.data
        if "width" in data and "height" in data:
            self.cv["width"]=self.data["width"]
            self.cv["height"]=self.data["height"]
            self.cv["scrollregion"]=(0,0,self.data["width"],self.data["height"])
        if "backcolor" in self.data:self.cv["bg"]=self.data["backcolor"]
    
    def undo(self,bell=False):
        if self.data["data"]:#如果还能撤销
            self._clearcanvas()
            self.data["data"].pop()
            self.draw()
            self.file_changed=True
        elif bell:self.master.bell()
    def onkey(self,event):
        if event.state==4:#按下Ctrl键
            if event.keysym=='z':#如果按下Ctrl+Z键
                self.undo()
            if event.keysym=='o':#按下Ctrl+O键
                self.ask_for_open()
            if event.keysym=='s':#Ctrl+S
                self.save()
    def setdefault(self):
        "将self.data设为默认,或填补其中不存在的键"
        self.data["ver"]=_ver
        if not "data" in self.data:self.data["data"]=[]
        if not "backcolor" in self.data:self.data["backcolor"]=_BACKCOLOR
        if not "strokecolor" in self.data:self.data["strokecolor"]=_STROKECOLOR
    
    @classmethod
    def new(cls):cls()
    def ask_for_open(self):
        returnval=self.ask_for_save(quit=False)
        if returnval==0:return
        
        filename=dialog.askopenfilename(master=self.master,
            filetypes=[_FILETYPE,("所有文件",'*')])
        if os.path.isfile(filename):
            self.filename=filename
            self._clearcanvas()
            self.openfile(filename)
    def openfile(self,filename):
        def toolarge(size):
            self.master.title("%s - 加载中,请耐心等待..." % _title)
            self.master.update()
        def onerror(err,lineno):
            msgbox.showinfo(type(err).__name__,
                            "无法将图像载入内存,您的文件可能已损坏: {}(line:{})"
                            .format((str(err) or "文件格式错误"),lineno))
        self.filename=filename
        self.data=DictFile(filename,toolarge_callback=toolarge,
                           error_callback=onerror)
        self.setdefault()
        self.draw()
        self.master.title("%s - %s" %(_title,self.filename))
    def ask_for_save(self,quit=True):
        if self.file_changed:
            retval=msgbox.askyesnocancel("文件尚未保存",
                              "是否保存{}的更改?".format(
                                  os.path.split(self.filename)[1] or "当前文件"))
            if not retval is None:
                if retval==True:self.save()
            else:return 0  #0:cancel
        if quit:self.quit()
    def save(self,filename=None):
        if not filename:
            if not self.filename:
                self.filename=dialog.asksaveasfilename(
                    filetypes=[_FILETYPE,("所有文件",'*')])
                if not self.filename:return
            filename=self.filename
        try:
            self.data["width"]=int(self.cv.winfo_width())
            self.data["height"]=int(self.cv.winfo_height())
        except tk.TclError:pass
        self.data.filename=filename
        self.data.save()
        self.file_changed=False
        self.master.title("%s - %s" %(_title,self.filename))
    
    def _clearcanvas(self):
        self.cv.delete("all")
    def clear(self):
        if not self.data["data"]:return
        if msgbox.askyesno("提示","是否清除?"):
            self._clearcanvas()
            self.data["data"]=[]
            self.data["backcolor"]=self.cv["bg"]=_BACKCOLOR
            self.file_changed=True
    def show_property_window(self):
        for window in PropertyWindow.instances:
            if window.master is self:
                window.focus_force()
                return
        PropertyWindow(self)
    def quit(self):
        for window in PropertyWindow.instances:
            if window.master is self:
                window.destroy()
                break
        Painter.instances.remove(self)
        self.master.destroy()

def main():
    if len(sys.argv)>1:
        for arg in sys.argv[1:]:
            try:
                root=tk.Tk()
                root.title(_title)
                window=Painter(root,filename=arg)
            except FileNotFoundError:msgbox.showwarning(
                "错误",
                "文件 {} 未找到".format(os.path.split(arg)[1]))
    else: Painter()
    tk.mainloop()

if __name__=="__main__":main()
