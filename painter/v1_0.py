import pprint,sys,os,pyobject
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as dialog
import tkinter.messagebox as msgbox

_ver="1.0"
_title="画板"
class Painter():
    def __init__(self,master=None,filename=""):
        if master==None:
            self.master=tk.Tk()
            self.master.title(_title)
        else:self.master=master
        self.master.bind("<Key>",self.onkey)
        self.file_changed=False
        self.filename=filename
        
        self.cv=tk.Canvas(self.master,relief=tk.RAISED,bg="white")
        self.cv.pack(expand=True,fill=tk.BOTH)
        self.cv.bind("<Button-1>",self.mousedown)
        self.cv.bind("<B1-Motion>",self.paint)
        self.cv.bind("<B1-ButtonRelease>",self.mouseup)
        
        self.cleanbtn=tk.Button(self.master,text="清除",command=self.clear)
        self.cleanbtn.pack(side=tk.LEFT)
        self.savebtn=tk.Button(self.master,text="保存",command=self.save)
        self.savebtn.pack(side=tk.LEFT)
        self.savebtn.bind("<Destroy>",self.ask_for_save)
        if self.filename:
            self.openfile(self.filename)
        else:self.data={"ver":_ver, "data":[]}
    
    def mousedown(self,event):
        data=self.data["data"]
        data.append([])#开始新的一根线
        data[-1].append((event.x,event.y))#将新绘制的点坐标附加在最近绘制的线末尾
    def paint(self,event):
        data=self.data["data"]
        self.cv.create_line(data[-1][-1][0],data[-1][-1][1],event.x,event.y)
        data[-1].append((event.x,event.y))
        self.file_changed=True
    def mouseup(self,event):
        if len(self.data["data"][-1])<=1:
            del self.data["data"][-1]
        pprint.pprint(self.data)

    def onkey(self,event):
        if event.state==4:#按下Ctrl键
            if event.keysym=='z':#如果按下Ctrl+Z键
                self.undo()
    def undo(self):
        if self.data["data"]:#如果还能撤销
            self.clearcanvas()
            self.data["data"].pop()
            self.draw()
            self.file_changed=True
    def draw(self,data=None):
        if not data:data=self.data["data"]
        for line in data:
            args=[]
            for dot in line:
                args.extend([dot[0],dot[1]])
            self.cv.create_line(*args)
    def setdefault(self):
        "将self.data设为默认,或填补其中没有的键"
        if not "ver" in self.data:self.data["ver"]=_ver
        if not "data" in self.data:self.data["data"]=[]
    def openfile(self,filename):
        f=open(filename)
        self.data={}
        while True:
            texts=f.readline().split(":")
            if not texts[0]:break
            if len(texts)>1:self.data[texts[0]]=eval(texts[1])
        self.setdefault()
        self.draw()
    def save(self,filename=None):
        if not filename:
            if not self.filename:
                self.filename=dialog.asksaveasfilename()
            filename=self.filename
        f=open(filename,'w')
        for key in self.data:
            f.write("{}:{}\n".format(key,repr(self.data[key])))
        self.file_changed=False
    def ask_for_save(self,event=None):
        pyobj.describe(event)
        #if not self.quited:
        #    self.quited=True
        if self.file_changed:
            returnval=msgbox.askyesnocancel("文件尚未保存",
                              "是否保存{}的更改?".format(os.path.split(self.filename)[1]))
            if returnval is None:
                self.draw()
                tk.mainloop()
            elif returnval:self.save()
    def _clearcanvas(self):
        length=0
        for line in self.data["data"]:
            length+=len(line)
        self.cv.delete(*range(1,length+1))
    def clear(self):
        if msgbox.askyesno("提示","是否清除?"):
            self._clearcanvas()
            self.data["data"]=[]
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
            except OSError:msgbox.showwarning(
                "错误",
                "文件{}未找到".format(os.path.split(self.filename)[1])
                )
    else:windows.append(Painter(filename="grass.vec"))
    tk.mainloop()

if __name__=="__main__":main()
