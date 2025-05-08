# 本版本加入了测试中的读写二进制文件功能
"""使用tkinter的Canvas控件制作的画板程序, 支持新建、打开、编辑和保存文档。
A painter that made by tkinter in Python.It supports new, open, edit and save documents."""
import sys,os, pickle,json
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as dialog
import tkinter.messagebox as msgbox
from tkinter.colorchooser import askcolor

try:
    from PIL import ImageGrab
except:ImageGrab=None

_ver="1.4.1"
__email__="3076711200@qq.com"
__author__="七分诚意 qq:3076711200"

def _load_icon(window,filename):
    #为window加载图标
    for availble_path in sys.path+[os.path.split(__file__)[0]]:
        try:
            window.iconbitmap("%s\\%s"%(availble_path,filename))
        except tk.TclError:pass

class ScrolledCanvas(tk.Canvas):
    """可滚动的画布,用法与默认的tkinter.Canvas完全相同。
继承自tkinter.Canvas类"""
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
        tk.Canvas.pack(self,side=tk.BOTTOM,expand=True,fill=tk.BOTH)
    def pack(self,**options):
        self.frame.pack(**options)
    def grid(self,**options):
        self.frame.grid(**options)
    def place(self,**options):
        self.frame.place(**options)
    def forget(self):
        self.frame.forget()

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
    def __init__(self,filename=None,mode='r',
                 encoding="utf-8",errors="strict",
                 error_callback=None,toolarge_callback=None,max_size=100000):
        self.closed=False
        dict.__init__(self)
        self.filename=filename
        if not filename:return
        self.file=open(filename,mode,encoding=encoding,errors=errors)
        lineno=0
        if os.path.getsize(filename)>max_size:
            if callable(toolarge_callback):toolarge_callback(len(texts[1]))
        while True:
            try:
                texts=self.file.readline().split(":")
                if not texts[0]:break
                lineno+=1
                if len(texts)>1:
                    self[texts[0]]=eval(texts[1],self)
            except Exception as err:
                if error_callback:error_callback(err,lineno)
                else:raise
        self.file.close()
    def save(self,filename=None,writeall=False,error_callback=None):
        if not filename:
            if not self.filename:return
            filename=self.filename
        try:
            self.file=open(filename,'w',encoding="utf_8")
            for key in self.keys():
                if writeall or (not key.startswith("__")):
                    self.file.write("{}:{}\n".format(key,repr(self[key])))
        except Exception as err:
            if error_callback:error_callback(err)
            else:raise
        finally:self.file.close()
    def close(self):
        self.save()
        self.closed=True

    def __iter__(self):
        return (key for key in dict.keys(self) if not key.startswith("__"))
    keys=__iter__
    @classmethod
    def fromdict(cls,dict,*args,**kwargs):
        new=cls(*args,**kwargs)
        for key in dict.keys():
            new[key]=dict[key]
        return new

class PropertyWindow(tk.Tk):
    #属性窗口
    instances=[]
    def __init__(self,master):
        self.init_window()
        self.master=master
        PropertyWindow.instances.append(self)
        self.create_widgets()
    def init_window(self):
        tk.Tk.__init__(self)
        self.title("文档属性")
        _load_icon(self,filename="property.ico")
        self.focus_force()
        #self.resizable(width=False,height=False)
        self.bind("<Destroy>",
                  lambda event:PropertyWindow.instances.remove(self)
                  if self in PropertyWindow.instances else None)
    def create_widgets(self):
        #创建控件
        size=tk.Frame(self)
        tk.Label(size,text="宽度(像素):").pack(side=tk.LEFT)
        self.width=tk.StringVar(self)
        bd=int(self.master.cv["bd"]) or 2 #画布的边框宽度
        self.width.set(self.master.data.get("width",
                                    self.master.cv.winfo_width()-bd*2))
        ttk.Entry(size,textvariable=self.width,width=10).pack(side=tk.LEFT)
        tk.Label(size,text="高度(像素):").pack(side=tk.LEFT)
        self.height=tk.StringVar(self)
        self.height.set(self.master.data.get("height",
                                             self.master.cv.winfo_height()-bd*2))
        ttk.Entry(size,textvariable=self.height,width=10).pack(side=tk.LEFT)
        size.pack(fill=tk.X,pady=2)

        ttk.Separator(self).pack(fill=tk.X,pady=2)
        backcolor=tk.Frame(self)
        tk.Label(backcolor,text="背景颜色:").pack(side=tk.LEFT)
        self.backcolor=tk.StringVar(self)
        self.backcolor.set(self.master.data.get("backcolor",''))
        ttk.Entry(backcolor,textvariable=self.backcolor).pack(side=tk.LEFT)
        ttk.Button(backcolor,text="...",width=2,
                   command=lambda:self.backcolor.set(
                       askcolor(master=self)[1] or self.backcolor.get())).pack(side=tk.LEFT)
        backcolor.pack(fill=tk.X,pady=2)

        strokecolor=tk.Frame(self)
        tk.Label(strokecolor,text="画笔颜色:").pack(side=tk.LEFT)
        self.strokecolor=tk.StringVar(self)
        self.strokecolor.set(self.master.data.get("strokecolor",''))
        ttk.Entry(strokecolor,textvariable=self.strokecolor).pack(side=tk.LEFT)
        ttk.Button(strokecolor,text="...",width=2,
                   command=lambda:self.strokecolor.set(
                       askcolor(master=self)[1] or self.strokecolor.get())).pack(side=tk.LEFT)
        strokecolor.pack(fill=tk.X,pady=2)

        pensize=tk.Frame(self)
        tk.Label(pensize,text="画笔粗细(像素): ").pack(side=tk.LEFT)
        self.pensize=ttk.Spinbox(pensize,from_=1,to=1000,width=16)
        self.pensize.set(self.master.data.get("pensize",1))
        self.pensize.pack(side=tk.LEFT)
        self.pensize.bind("<Key-Return>",self.confirm)
        pensize.pack(fill=tk.X,pady=2)

        self.setdefault=tk.IntVar(self)
        ttk.Checkbutton(self,text="设为默认值",variable=self.setdefault).pack(
            side=tk.LEFT,pady=2)

        buttons=tk.Frame(self)
        ttk.Button(buttons,text="确定",width=6,command=self.confirm).pack(
            side=tk.LEFT,padx=12)
        ttk.Button(buttons,text="取消",width=6,command=self.destroy).pack(
            side=tk.LEFT,padx=12)
        buttons.pack(side=tk.RIGHT,pady=2)
    def confirm(self,event=None):
        newproperty={}
        newproperty["width"]=int(self.width.get())
        newproperty["height"]=int(self.height.get())
        newproperty["backcolor"]=self.backcolor.get()
        newproperty["strokecolor"]=self.strokecolor.get()
        newproperty["pensize"]=int(self.pensize.get())
        self.master.data.update(newproperty)
        self.master.draw()
        self.master.file_changed=True

        if self.setdefault.get():
            self.master.config.update(newproperty)
        self.destroy()

class Painter():
    instances=[]
    TITLE="画板 v"+_ver
    CONFIGFILE=os.getenv("userprofile")+"\.painter\config.cfg"
    #CONFIG:包含默认的工具栏位置,背景颜色,画笔颜色,画笔粗细
    CONFIG={"toolbar":"bottom","backcolor":"white",
            "strokecolor":"black","pensize":1}
    FILETYPE=("vec矢量图文件 (*.vec)","*.vec")
    _FILETYPES=(FILETYPE,("pickle文件 (*.pkl;*.pickle)","*.pkl;*.pickle"),
                ("json对象 (*.json)","*.json"),("二进制文件 (*.dat)","*.dat")
                ,("所有文件","*.*"))
    _SAVE_FILETYPES=(("bmp图像 (*.bmp)","*.bmp"),
                    ("jpeg图像( *.jpg)","*.jpg"),
                    ("gif图像 (*.gif)","*.gif"),
                    ("png图像 (*.png)","*.png"))+_FILETYPES
    def __init__(self,master=None,filename=""):
        if master==None:
            self.master=tk.Tk()
            self.master.title(self.TITLE)
        else:self.master=master
        self.master.focus_force()
        _load_icon(self.master,filename="paint.ico")
        self.master.bind("<Key>",self.onkey)
        self.master.bind("<FocusIn>",self.focus)
        self.master.bind("<FocusOut>",self.focus)
        self.master.protocol("WM_DELETE_WINDOW",self.ask_for_save)
        self.file_changed=False
        self.filename=filename
        Painter.instances.append(self)
        self.load_config()

        self.create_toolbar()
        self.create_canvas()
        self.create_menu()
        if self.filename:
            self.openfile(self.filename)
        else:
            self.data=DictFile()
            self.setdefault()
            self.draw()
    def load_config(self):
        #创建一个配置文件
        try:self.config=DictFile(self.CONFIGFILE)
        except:
            #配置文件不存在时
            try:
                try:os.mkdir(os.getenv("userprofile")+"\.painter")
                except FileExistsError:pass
                open(self.CONFIGFILE,'w')
            except OSError:
                self.config=DictFile.fromdict(self.CONFIG)
            else:
                self.config=DictFile(self.CONFIGFILE)
                self.config.update(self.CONFIG)
    def create_canvas(self):
        #创建画布
        self.cv=ScrolledCanvas(self.master,bg="white",
                          cursor="pencil",relief=tk.GROOVE)
        try:
            self.cv["cursor"]="@pencil.cur"
        except tk.TclError:
            self.cv["cursor"]="pencil"
        self.cv.pack(side=tk.BOTTOM,expand=True,fill=tk.BOTH)
        self.cv.bind("<Button-1>",self.mousedown)
        self.cv.bind("<B1-Motion>",self.paint)
        self.cv.bind("<B1-ButtonRelease>",self.mouseup)
        self.cv.bind("<Button-3>",
                     lambda event:self.editmenu.post(event.x_root,event.y_root))
    def create_menu(self):
        #创建菜单
        menu=tk.Menu(self.master)
        filemenu=tk.Menu(self.master,tearoff=False)
        filemenu.add_command(label="新建",
                             command=self.new,accelerator="Ctrl+N")
        filemenu.add_command(label="打开",
                             command=self.ask_for_open,accelerator="Ctrl+O")
        filemenu.add_command(label="保存",
                             command=self.save,accelerator="Ctrl+S")
        filemenu.add_command(label="另存为",command=self.save_as)
        filemenu.add_separator()
        filemenu.add_command(label="退出",command=self.ask_for_save)

        self.editmenu=tk.Menu(self.cv,tearoff=False)
        self.editmenu.add_command(label="撤销",state=tk.DISABLED,
                              command=self.undo)
        self.editmenu.add_command(label="清除",command=self.clear)
        self.editmenu.add_separator()
        self.editmenu.add_command(label="文档属性",
                              command=self.show_property_window)

        helpmenu=tk.Menu(self.master,tearoff=False)
        helpmenu.add_command(label="关于",command=self.about)

        menu.add_cascade(label="文件",menu=filemenu)
        menu.add_cascade(label="编辑",menu=self.editmenu)
        menu.add_cascade(label="帮助",menu=helpmenu)
        # 显示菜单
        self.master.config(menu=menu)

    def create_toolbar(self):
        #创建工具栏
        self.toolbar=tk.Frame(self.master,bg="gray92")
        self.toolbar.pack(
            side=self.config.get("toolbar",tk.BOTTOM),fill=tk.X)
        self.create_toolbutton(self.toolbar)
        self.toolbar_bind()
    def create_toolbutton(self,master):
        #创建工具栏按钮
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
        self.toolbar.config(bg="#cfd7e2",cursor="fleur")
    def move_toolbar(self,event):
        #移动工具栏
        if event.y<-int(self.cv.winfo_height()-20):#置于窗口上方
            self.cv.forget();self.toolbar.forget()
            self.toolbar.pack(side=tk.TOP,fill=tk.X)
            self.cv.pack(side=tk.TOP,expand=True,fill=tk.BOTH)
            self.config["toolbar"]=tk.TOP
        elif event.y>int(self.cv.winfo_height()-20):#置于窗口下方
            self.cv.forget();self.toolbar.forget()
            self.toolbar.pack(side=tk.BOTTOM,fill=tk.X)
            self.cv.pack(side=tk.BOTTOM,expand=True,fill=tk.BOTH)
            self.config["toolbar"]=tk.BOTTOM
    def toolbar_mouseup(self,event):
        self.toolbar.config(bg="gray92",cursor="arrow")

    def mousedown(self,event):
        data=self.data["data"]
        data.append([])#开始新的一根线
        #将新绘制的点坐标附加在最近绘制的线末尾
        data[-1].append((event.x,event.y))
    def paint(self,event):
        data=self.data["data"]
        try:
            x=data[-1][-1][0];y=data[-1][-1][1]
            #在画布上创建新的线条
            self.cv.create_line(x,y,event.x,event.y,joinstyle=tk.ROUND,
                                width=self.data["pensize"],
                                capstyle=tk.ROUND,fill=self.data["strokecolor"])
            data[-1].append((event.x,event.y))
            self.file_changed=True
            self.editmenu.entryconfig(0,state=tk.NORMAL)
        except IndexError:pass
    def mouseup(self,event):
        try:
            if len(self.data["data"][-1])<=1:
                del self.data["data"][-1]
        except IndexError:pass
    def draw(self,data=None):
        #根据self.data的内容绘制图形
        if not data:data=self.data
        self._clearcanvas()
        self.config_canvas(data)
        for line in data["data"]:
            args=[]
            for dot in line:
                args.extend([dot[0],dot[1]])
            self.cv.create_line(*args,joinstyle=tk.ROUND,
                                width=self.data["pensize"],
                                capstyle=tk.ROUND,fill=self.data["strokecolor"])
    def config_canvas(self,data=None):
        if not data:data=self.data
        if "width" in data and "height" in data:
            self.cv.configure(width=self.data["width"],
                height=self.data["height"],
                scrollregion=(0,0,self.data["width"],self.data["height"]))
        if "backcolor" in self.data:self.cv.config(bg=self.data["backcolor"])

    def undo(self):
        if self.data["data"]:#如果还能撤销
            self._clearcanvas()
            self.data["data"].pop()
            self.draw()
            self.file_changed=True
        else:
            self.master.bell()
            self.editmenu.entryconfig(0,
                    state=(tk.NORMAL if self.data["data"] else tk.DISABLED))
    def onkey(self,event):
        if event.state==4:#按下Ctrl键
            if event.keysym=='z':#如果按下Ctrl+Z键
                self.undo()
            elif event.keysym=='o':#按下Ctrl+O键
                self.ask_for_open()
            elif event.keysym=='s':#Ctrl+S
                self.save()
            elif event.keysym=='n': #Ctrl+N
                self.new()
    def setdefault(self):
        "将self.data设为默认,或填补其中不存在的键"
        self.data.setdefault("ver",_ver)
        self.data.setdefault("data",[])
        self.data.setdefault("pensize",
                             self.config.get("pensize",self.CONFIG["pensize"]))
        self.data.setdefault("backcolor",
                    self.config.get("backcolor",self.CONFIG["backcolor"]))
        self.data.setdefault("strokecolor",
                    self.config.get("strokecolor",self.CONFIG["strokecolor"]))

    @classmethod
    def new(cls):
        "新建一个文件(打开另一个画板窗口)"
        cls()
    def ask_for_open(self):
        returnval=self.ask_for_save(quit=False)
        if returnval==0:return
        #弹出打开对话框
        filename=dialog.askopenfilename(master=self.master,
                                        filetypes=self._FILETYPES)
        if os.path.isfile(filename):
            self.filename=filename
            self._clearcanvas()
            self.openfile(filename)
    def openfile(self,filename):
        "打开一个文件"
        def toolarge(size):
            self.master.title("%s - 加载中,请耐心等待..." % self.TITLE)
            self.master.update()
        def onerror(err,lineno="未知"):
            #显示错误消息
            msgbox.showinfo(type(err).__name__,
                            "无法将图像载入内存,您的文件可能已损坏: {}(行 {})"
                            .format((str(err) or "文件格式错误"),lineno))
        def load(filename,mode,use_module):
            #加载pickle或json文件
            try:
                f=open(filename,mode)
                obj=use_module.load(f)
                if type(obj) is dict:
                    return DictFile.fromdict(obj)
                elif type(obj) in (list,tuple):
                    if type(obj) is tuple:obj=list(obj)
                    data={"data":obj}
                else:
                    raise TypeError("未知数据类型: %r"%type(obj))
            except Exception as err:onerror(err)

        self.filename=filename
        if filename.endswith(".pkl") or filename.endswith(".pickle"):
            self.data=load(filename,'rb',use_module=pickle)
        elif filename.endswith(".json"):
            self.data=load(filename,'r',use_module=json)
        elif filename.endswith(".dat"):
            self.open_datfile(filename)
        else:
            self.data=DictFile(filename,toolarge_callback=toolarge,
                               error_callback=onerror)
        self.setdefault()
        self.draw()
        self.master.title("%s - %s" %(self.TITLE,self.filename))
        self.editmenu.entryconfig(0,
                    state=(tk.NORMAL if self.data["data"] else tk.DISABLED))
        if self.data.get("ver",_ver).strip() > _ver:
            msgbox.showinfo("警告","""文件版本过高, 某些内容可能无法正常显示。
当前版本: {}\n文件版本: {}""".format(_ver,self.data["ver"]))
    def open_datfile(self,filename):
        # 用于支持二进制文件读取。二进制文件比文本文件体积更小。

        class Stop(Exception):pass
        def decode(bytes,signed=True):
            # 用于将二进制字节转为整数。signed:有无符号
            return int.from_bytes(bytes,'big',signed=signed)

        def read_int(fileobj,len=2):
            # 从二进制文件中读取一个整数。
            byte=fileobj.read(len)
            if byte==b'':raise EOFError
            num=decode(byte)
            if num==-1:raise Stop # 如decode(b'\xff\xff')结果为-1
            return num

        def read_obj(fileobj,coding="utf-8"):
            # 从二进制文件中读取一个字符串，再用eval转换成python对象。
            # 每读取一次，fileobj的偏移量会改变，便于下一次读取
            len=decode(fileobj.read(2),signed=False)
            if len==65535:raise Stop # 遇到停止标志ff ff
            return eval(str(fileobj.read(len),encoding=coding))

        self.data=DictFile()
        f=open(filename,'rb')
        if f.read(3)!=b'VEC': # 判断文件头
            msgbox.showinfo("","不是一个vec文件")
            return
        try:
            # 读取文件头数据
            while True:
                key=read_obj(f) # 读取键
                value=read_obj(f) # 读取值
                print(key,value)
                self.data[key]=value
        except Stop:pass
        # 读取文件的数据部分
        self.data['data']=[]
        while True:
            line=[]
            try:
                while True:
                    dot=(read_int(f),read_int(f)) # 连续读取2个整数
                    line.append(dot)
            except Stop:
                self.data['data'].append(line)
            except EOFError:break

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
        "保存文件"
        def onerror(err):
            msgbox.showinfo(type(err).__name__,
                        "抱歉, 无法保存文件: {}".format(str(err)))
        def dump(filename,mode,use_module):
            try:
                f=open(filename,mode)
                use_module.dump(dict(self.data),f)
                f.close()
            except Exception as err:onerror(err)

        if not filename:
            if not self.filename:
                self.filename=dialog.asksaveasfilename(master=self.master,
                    filetypes=self._SAVE_FILETYPES)
                if not self.filename:return
            filename=self.filename
        try:
            bd=int(self.cv["bd"]) or 2 #边框宽度
            self.data["width"]=int(self.cv.winfo_width())-bd*2
            self.data["height"]=int(self.cv.winfo_height())-bd*2
        except tk.TclError:pass

        if filename.endswith(".pkl") or filename.endswith(".pickle"):
            dump(filename,'wb',use_module=pickle)
        elif filename.endswith(".json"):
            dump(filename,'w',use_module=json)
        elif filename.endswith(".dat"):
            self.save_datfile(filename)
        elif filename.endswith((".png",".jpg",".gif")):
            x1=self.cv.winfo_rootx()+bd
            y1=self.cv.winfo_rooty()+bd
            x2=x1+self.cv.winfo_width()-bd*2
            y2=y1+self.cv.winfo_height()-bd*2
            pic = ImageGrab.grab(bbox=(x1,y1,x2,y2))
            pic.save(filename)
        else:
            self.data.save(filename,error_callback=onerror)
        self.file_changed=False
        self.master.title("%s - %s" %(self.TITLE,self.filename))
    def save_as(self):
        filename=dialog.asksaveasfilename(master=self.master,
                    filetypes=self._SAVE_FILETYPES,defaultextension='.vec')
        if filename:
            self.save(filename)
            self.filename=filename
    def save_datfile(self,filename):
        # 保存为二进制文件
        def encode(num,len=2,signed=True):# 用于将整数转为二进制字节。
            return num.to_bytes(len,'big',signed=signed)
        def encode_obj(obj,coding='utf-8'): # 将对象写入二进制文件。
            string=repr(obj)
            return encode(len(string),signed=False)+bytes(string,coding)

        f=open(filename,'wb')
        f.write(b'VEC') # 文件头
        for key in self.data:
            if not key=="data":
                f.write(encode_obj(key)+encode_obj(self.data[key]))
        f.write(b'\xff\xff')
        for line in self.data['data']:
            for dot in line:
                f.write(encode(dot[0])+encode(dot[1])) # 写入数据
            f.write(b'\xff\xff')
        f.close()
    def _clearcanvas(self):
        #清除画布
        self.cv.delete("all")
    def clear(self):
        if not self.data["data"]:return
        if msgbox.askyesno("提示","是否清除?",parent=self.master):
            self._clearcanvas()
            self.data["data"]=[]
            self.file_changed=True
            self.editmenu.entryconfig(0,state=tk.DISABLED)
    def show_property_window(self):
        for window in PropertyWindow.instances:
            if window.master is self:
                window.focus_force()
                return
        PropertyWindow(self)
    def focus(self,event):
        #当窗口获得或失去焦点时,调用此函数
        for window in PropertyWindow.instances:
            if window.master is self:
                if event.type==tk.EventType.FocusIn:
                    if window.wm_state()=="iconic":
                        window.deiconify()
                    window.focus_force()
                else:
                    if self.master.wm_state()=="iconic":
                        window.iconify()
                break
    def quit(self):
        for window in PropertyWindow.instances:
            if window.master is self:
                window.destroy()
                break
        Painter.instances.remove(self)
        self.config.close()
        self.master.destroy()

    def about(self):
        msgbox.showinfo("关于",__doc__+"\n作者: "+__author__,parent=self.master)

def main():
    try:os.chdir(os.path.split(__file__)[0])
    except OSError:pass
    if len(sys.argv)>1:
        for arg in sys.argv[1:]:
            try:
                root=tk.Tk()
                root.title(Painter.TITLE)
                window=Painter(root,filename=arg)
            except FileNotFoundError:msgbox.showwarning(
                "错误",
                "文件 {} 未找到".format(os.path.split(arg)[1]))
    else: Painter()
    tk.mainloop()

if __name__=="__main__":main()
