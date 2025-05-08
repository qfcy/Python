import pprint,sys,os,pyobject
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as dialog
import tkinter.messagebox as msgbox

_ver="1.1"
_title="画板"
_BACKCOLOR="white"
_FILETYPE=("vec矢量图文件(*.vec)","*.vec")
class Painter():
    def __init__(self,master=None,filename=""):
        if master==None:
            self.master=tk.Tk()
            self.master.title(_title)
        else:self.master=master
        self.master.bind("<Key>",self.onkey)
        self.file_changed=False
        self.filename=filename
        
        self.create_canvas()

        self.toolbar=tk.Frame()
        self.toolbar.pack(side=tk.BOTTOM,fill=tk.X)
        self.create_toolbar(self.toolbar)
        if self.filename:
            self.openfile(self.filename)
        else:self.data={"ver":_ver, "data":[]}
    def create_canvas(self):
        self.cv=tk.Canvas(self.master,relief=tk.GROOVE,bg="white")
        self.cv.pack(side=tk.TOP,expand=True,fill=tk.BOTH)
        self.cv.bind("<Button-1>",self.mousedown)
        self.cv.bind("<B1-Motion>",self.paint)
        self.cv.bind("<B1-ButtonRelease>",self.mouseup)
    
    def create_toolbar(self,master=None,buttonside=tk.BOTTOM):
        if not master:
            self.toolbar=master=tk.Frame(bg="gray93")
            self.toolbar.pack(side=side,fill=tk.X)
        self.master.update()
        self.newbtn=tk.Button(master,text="新建",command=self.ask_for_open)
        self.newbtn.pack(side=tk.LEFT)
        self.openbtn=tk.Button(master,text="打开",command=self.ask_for_open)
        self.openbtn.pack(side=tk.LEFT)
        self.savebtn=tk.Button(master,text="保存",command=self.save)
        self.savebtn.pack(side=tk.LEFT)
        self.savebtn.bind("<Destroy>",self.ask_for_save)
        self.cleanbtn=tk.Button(master,text="清除",command=self.clear)
        self.cleanbtn.pack(side=tk.LEFT)
        print("Toolbar:",self.toolbar,master)
        self.toolbar.bind("<Button-1>",self.toolbar_mousedown)
        self.toolbar.bind("<B1-Motion>",self.move_toolbar)
        self.toolbar.bind("<B1-ButtonRelease>",self.toolbar_mouseup)
    def toolbar_mousedown(self,event):self.toolbar["bg"]="grey81"
    def move_toolbar(self,event):
        print(event.x,event.y)
        if event.y<-int(self.cv["height"]):
            #self.toolbar.forget()
            self.toolbar.place(x=0,y=0,width=self.master.winfo_width())
        if event.y>int(self.cv["height"]):
            #self.toolbar.forget()
            self.toolbar.place(x=0,y=self.master.winfo_height()-25,
                               width=self.master.winfo_width())
        self.master.update()
    def toolbar_mouseup(self,event):self.toolbar["bg"]="gray93"
    
    def mousedown(self,event):
        data=self.data["data"]
        data.append([])#开始新的一根线
        data[-1].append((event.x,event.y))#将新绘制的点坐标附加在最近绘制的线末尾
    def paint(self,event):
        data=self.data["data"]
        try:
            x=data[-1][-1][0];y=data[-1][-1][1]
            self.cv.create_line(x,y,event.x,event.y)
            data[-1].append((event.x,event.y))
            self.file_changed=True
        except IndexError:pass
    def mouseup(self,event):
        try:
            if len(self.data["data"][-1])<=1:
                del self.data["data"][-1]
        except IndexError:pass
        print(self.cv.winfo_width())
    def draw(self,data=None):
        if not data:data=self.data["data"]

        if "width" in self.data:self.cv["width"]=self.data["width"]
        if "height" in self.data:self.cv["height"]=self.data["height"]
        if "backcolor" in self.data:self.cv["bg"]=self.data["backcolor"]
        for line in data:
            args=[]
            for dot in line:
                args.extend([dot[0],dot[1]])
            self.cv.create_line(*args)
    def undo(self):
        if self.data["data"]:#如果还能撤销
            self.clearcanvas()
            self.data["data"].pop()
            self.draw()
            self.file_changed=True

    
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
    
    def ask_for_open(self):
        self.ask_for_save()
        filename=dialog.askopenfilename(filetypes=[_FILETYPE,("所有文件",'*')])
        if os.path.isfile(filename):
            self.filename=filename
            self._clearcanvas()
            self.openfile(filename)
    def openfile(self,filename):
        f=open(filename)
        self.data={}
        while True:
            try:
                texts=f.readline().split(":")
                if not texts[0]:break
                if len(texts)>1:self.data[texts[0]]=eval(texts[1])
            except Exception as err:
                msgbox.showinfo(type(err).__name__,
                                "无法将图像载入内存,您的文件可能已损坏: {}"
                                .format(err.msg or "文件格式错误"))
        self.setdefault()
        self.draw()
    def ask_for_save(self,event=None):
        pyobject.describe(event,verbose=False)
        #if not self.quited:
        #    self.quited=True
        if self.file_changed:
            retval=msgbox.askyesno("文件尚未保存",
                              "是否保存{}的更改?".format(os.path.split(self.filename)[1]))
            if retval:self.save()
            #elif retval is None:
            #    self.create_canvas()
            #    tk.mainloop()
    def save(self,filename=None):
        if not filename:
            if not self.filename:
                self.filename=dialog.asksaveasfilename(
                    filetypes=[_FILETYPE,("所有文件",'*')])
                if not self.filename:return
            filename=self.filename
        self.data["width"]=int(self.cv["width"])
        self.data["height"]=int(self.cv["height"])
        f=open(filename,'w')
        for key in self.data:
            f.write("{}:{}\n".format(key,repr(self.data[key])))
        self.file_changed=False
    
    def _clearcanvas(self):
        length=0
        for line in self.data["data"]:
            length+=len(line)
        self.cv.delete(*range(1,length+1))
    def clear(self):
        if msgbox.askyesno("提示","是否清除?"):
            self._clearcanvas()
            self.data["data"]=[]
            self.data["backcolor"]=self.cv["bg"]=_BACKCOLOR
            self.file_changed=True
                  
def main():
    windows=[]
    if len(sys.argv)>1:
        for n in range(1,len(sys.argv)):
            try:
                root=tk.Tk()
                root.title(_title)
                window=Painter(root,filename=sys.argv[n])
                windows.append(window)
            except FileNotFoundError:msgbox.showwarning(
                "错误",
                "文件{}未找到".format(os.path.split(self.filename)[1])
                )
    else:windows.append(Painter())
    tk.mainloop()

if __name__=="__main__":main()
