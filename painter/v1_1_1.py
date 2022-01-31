import sys,os
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as dialog
import tkinter.messagebox as msgbox

_ver="1.1.1"
_title="画板 v"+_ver
_BACKCOLOR="white"
_FILETYPE=("vec矢量图文件(*.vec)","*.vec")
_windows=[]
class Painter():
    def __init__(self,master=None,filename=""):
        if master==None:
            self.master=tk.Tk()
            self.master.title(_title)
        else:self.master=master
        self.master.bind("<Key>",self.onkey)
        self.master.protocol("WM_DELETE_WINDOW",self.ask_for_save)
        self.file_changed=False
        self.filename=filename

        self.toolbar=tk.Frame(self.master,bg="gray92")
        self.toolbar.pack(side=tk.BOTTOM,fill=tk.X)
        self.create_toolbar(self.toolbar)
        self.create_canvas()
        self.create_menu()
        if self.filename:
            self.openfile(self.filename)
        else:self.data={"ver":_ver, "data":[]}
    def create_canvas(self):
        self.cv=tk.Canvas(self.master,bg="white",
                          cursor="pencil",relief=tk.GROOVE)
        self.cv.pack(side=tk.BOTTOM,expand=True,fill=tk.BOTH)
        self.cv.bind("<Button-1>",self.mousedown)
        self.cv.bind("<B1-Motion>",self.paint)
        self.cv.bind("<B1-ButtonRelease>",self.mouseup)
        self.cv.bind("<Button-3>",
                     lambda event:self.menu.post(event.x_root,event.y_root))
    def create_menu(self):
        self.menu=tk.Menu(self.cv,tearoff=False)
        self.menu.add_command(label="撤销",command=lambda:self.undo(bell=True))
        self.menu.add_separator()
        self.menu.add_command(label="清除",command=self.clear)
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
    def toolbar_bind(self):
        self.toolbar.bind("<Button-1>",self.toolbar_mousedown)
        self.toolbar.bind("<B1-Motion>",self.move_toolbar)
        self.toolbar.bind("<B1-ButtonRelease>",self.toolbar_mouseup)
    def toolbar_mousedown(self,event):
        self.toolbar.config(bg="grey81",cursor="fleur")
    def move_toolbar(self,event):
        if event.y<-int(self.cv["height"]):#置于窗口下方
            self.cv.forget();self.toolbar.forget()
            self.toolbar.pack(side=tk.TOP,fill=tk.X)
            self.cv.pack(side=tk.TOP,expand=True,fill=tk.BOTH)
        elif event.y>int(self.cv["height"]):#置于窗口上方
            self.cv.forget();self.toolbar.forget()
            self.toolbar.pack(side=tk.BOTTOM,fill=tk.X)
            self.cv.pack(side=tk.BOTTOM,expand=True,fill=tk.BOTH)
        self.master.update()
    def toolbar_mouseup(self,event):
        self.toolbar.config(bg="gray92",cursor="arrow")
##    def toolbutton_destroy(self):
##        self.newbtn.destroy()
##        self.openbtn.destroy()
##        self.savebtn.destroy()
##        self.cleanbtn.destroy()
    def mousedown(self,event):
        data=self.data["data"]
        data.append([])#开始新的一根线
        data[-1].append((event.x,event.y))#将新绘制的点坐标附加在最近绘制的线末尾
    def paint(self,event):
        data=self.data["data"]
        try:
            x=data[-1][-1][0];y=data[-1][-1][1]
            self.cv.create_line(x,y,event.x,event.y,
                                joinstyle=tk.ROUND,capstyle=tk.ROUND)
            data[-1].append((event.x,event.y))
            self.file_changed=True
        except IndexError:pass
    def mouseup(self,event):
        try:
            if len(self.data["data"][-1])<=1:
                del self.data["data"][-1]
        except IndexError:pass
    def draw(self,data=None):
        if not data:data=self.data["data"]

        if "width" in self.data:self.cv["width"]=self.data["width"]
        if "height" in self.data:self.cv["height"]=self.data["height"]
        if "backcolor" in self.data:self.cv["bg"]=self.data["backcolor"]
        for line in data:
            args=[]
            for dot in line:
                args.extend([dot[0],dot[1]])
            self.cv.create_line(*args,joinstyle=tk.ROUND,capstyle=tk.ROUND)
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
        "将self.data设为默认,或填补其中没有的键"
        self.data["ver"]=_ver
        if not "data" in self.data:self.data["data"]=[]
        if not "backcolor" in self.data:self.data["backcolor"]=_BACKCOLOR
    @classmethod
    def new(cls):
        _windows.append(cls())
        
    def ask_for_open(self):
        returnval=self.ask_for_save(quit=False)
        if returnval==0:return
        
        filename=dialog.askopenfilename(filetypes=[_FILETYPE,("所有文件",'*')])
        if os.path.isfile(filename):
            self.filename=filename
            self._clearcanvas()
            self.openfile(filename)
    def openfile(self,filename):
        f=open(filename)
        self.data={}
        lineno=0
        while True:
            try:
                texts=f.readline().split(":")
                if not texts[0]:break
                lineno+=1
                if len(texts)>1:
                    if len(texts[1])>100000:
                        self.master.title("%s - 加载中,请耐心等待..." % _title)
                        self.master.update()
                    self.data[texts[0]]=eval(texts[1])
            except Exception as err:
                msgbox.showinfo(type(err).__name__,
                                "无法将图像载入内存,您的文件可能已损坏: {}(line:{})"
                                .format((str(err) or "文件格式错误"),lineno))
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
        if quit:
            _windows.remove(self)
            self.master.destroy()
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

        f=open(filename,'w')
        for key in self.data:
            f.write("{}:{}\n".format(key,repr(self.data[key])))
        self.file_changed=False
    
    def _clearcanvas(self):
        self.cv.delete("all")
    def clear(self):
        if not self.data["data"]:return
        if msgbox.askyesno("提示","是否清除?"):
            self._clearcanvas()
            self.data["data"]=[]
            self.data["backcolor"]=self.cv["bg"]=_BACKCOLOR
            self.file_changed=True
                  
def main():
    if len(sys.argv)>1:
        for n in range(1,len(sys.argv)):
            try:
                root=tk.Tk()
                root.title(_title)
                window=Painter(root,filename=sys.argv[n])
                _windows.append(window)
            except FileNotFoundError:msgbox.showwarning(
                "错误",
                "文件{}未找到".format(os.path.split(self.filename)[1])
                )
    else:_windows.append(Painter())
    tk.mainloop()

if __name__=="__main__":main()
