"以图形方式浏览Python对象的模块。A module providing a visual interface to browse Python objects."
import sys,os,types,typing,ctypes
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as msgbox
import tkinter.simpledialog as simpledialog
from inspect import isfunction,ismethod,isgeneratorfunction,isgenerator,iscode
try:from pyobject import objectname,_shortrepr
except ImportError:from __init__ import objectname,_shortrepr

_IMAGE_PATH=os.path.join(os.path.split(__file__)[0],"images")

def isfunc(obj):
    # 判断一个对象是否为函数或方法
    if isfunction(obj) or ismethod(obj):return True
    # 使用typing而不用types.WrapperDescriptorType是为了与旧版本兼容
    func_types=[types.LambdaType,types.BuiltinFunctionType,
                types.BuiltinMethodType,typing.WrapperDescriptorType,
                typing.MethodWrapperType,typing.MethodDescriptorType]
    if sys.version_info.minor>=7:
        ClassMethodDescriptorType=types.ClassMethodDescriptorType
    else: # 3.7之前的旧版本
        ClassMethodDescriptorType=type(dict.__dict__['fromkeys'])
    func_types.append(ClassMethodDescriptorType)
    for type in func_types:
        if isinstance(obj,type):
            return True
    return False
def isdict(obj):
    # 判断一个对象是否为字典
    dict_types=[dict,types.MappingProxyType]
    for type in dict_types:
        if isinstance(obj,type):return True
    return False

def get_dpi_scale():
    # 获取Windows的当前DPI，仅Windows可用
    hdc = ctypes.windll.user32.GetDC(0)
    dpi_x = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)  # 88: LOGPIXELSX
    dpi_y = ctypes.windll.gdi32.GetDeviceCaps(hdc, 90)  # 90: LOGPIXELSY
    ctypes.windll.user32.ReleaseDC(0, hdc)
    return dpi_x/96, dpi_y/96

class ScrolledTreeview(ttk.Treeview):
    "A scrollable Treeview widget inherited from ttk.Treeview."
    def __init__(self,master,**options):
        self.frame=tk.Frame(master)
        ttk.Treeview.__init__(self,self.frame,**options)

        self.hscroll=ttk.Scrollbar(self.frame,orient=tk.HORIZONTAL,
                                   command=self.xview)
        self.vscroll=ttk.Scrollbar(self.frame,command=self.yview)
        self["xscrollcommand"]=self.hscroll.set
        self["yscrollcommand"]=self.vscroll.set
        #self.hscroll.pack(side=tk.BOTTOM,fill=tk.X)
        self.vscroll.pack(side=tk.RIGHT,fill=tk.Y)
        ttk.Treeview.pack(self,side=tk.BOTTOM,expand=True,fill=tk.BOTH)
    def pack(self,**options):
        self.frame.pack(**options)
    def grid(self,**options):
        self.frame.grid(**options)
    def place(self,**options):
        self.frame.place(**options)

class ObjectBrowser():
    title="Python Object Browser"
    def __init__(self,master,obj,verbose=False,name="obj",
                 multi_window=False,refresh_history=True,
                 root_obj=None,rootobj_name=None):
        self.master=master
        self.verbose=verbose
        self.name=name
        self.multi_window=multi_window # 是否多窗口
        self.refresh_history=refresh_history
        self.root_obj = root_obj if root_obj is not None else obj # 根对象的名称，用于历史记录
        self.rootobj_name = rootobj_name or name
        self.history=[(obj,name)] # 单窗口浏览的历史记录，由多个(对象，路径)的元组组成
        self.history_index=0

        self.master.title(self.title)
        try:
            self.master.iconbitmap(os.path.join(_IMAGE_PATH,"python.ico"))
        except tk.TclError:pass
        self.load_image()
        self.create_widgets()
        self.browse(obj,name=name)
    def create_widgets(self):
        # 创建控件
        toolbar=tk.Frame(self.master)
        if not self.multi_window:
            tk.Button(toolbar,image=self.back_image,command=self.back).pack(side=tk.LEFT)
            tk.Button(toolbar,image=self.forward_image,command=self.forward).pack(side=tk.LEFT)
        tk.Button(toolbar,image=self.refresh_image,command=self.navigate_history #refresh
                    ).pack(side=tk.LEFT)
        self.label=tk.Label(toolbar,anchor="w")
        self.label.pack(side=tk.LEFT,fill=tk.X)
        toolbar.pack(side=tk.TOP,fill=tk.X)
        self.tvw=ScrolledTreeview(self.master,column='.',selectmode=tk.EXTENDED)
        self.tvw.heading("#0",text="Attribute/Index/Key")
        self.tvw.heading("#1",text="Value")
        self.tvw.column("#0", stretch = 0, # 不跟随窗口大小的变化拉伸
                        width = int(160*(get_dpi_scale()[0] if sys.platform == "win32" else 1)))
        self.tvw.column("#1", stretch=1)
        self.tvw.bind("<<TreeviewSelect>>",self.on_select)
        self.tvw.bind("<Double-Button-1>",self.on_open)
        self.tvw.bind("<Key-Return>",self.on_open)
        self.tvw.bind("<Key-Delete>",self.del_item)
        self.tvw.tag_configure("error",foreground="red") # 经测试, Python 3.7-3.9中无法显示颜色效果(bug?)
        self.master.bind("<F5>",self.navigate_history) #refresh)

        self.functions_tag=self.tvw.insert('',index=0,text="Functions/Methods")
        self.attributes_tag=self.tvw.insert('',index=1,text="Attributes")
        self.classes_tag=self.tvw.insert('',index=2,text="Classes")
        self.lst_tag=self.tvw.insert('',index=3,text="List data")
        self.dict_tag=self.tvw.insert('',index=4,text="Dictionary data")
        self.tvw.item(self.attributes_tag,open=True) # 展开项
        self.tvw.item(self.classes_tag,open=True)
        self.tvw.item(self.lst_tag,open=True)
        self.tvw.item(self.dict_tag,open=True)
        if sys.platform == "win32": # 高dpi支持
            style = ttk.Style(self.master)
            style.configure("Treeview", rowheight=int(20*get_dpi_scale()[1]))

        editor = ttk.Labelframe(self.master, text='Edit value',
                                width=100, height=100)
        self.okbtn=ttk.Button(editor,text="OK",
                              command=self.ok_click,state=tk.DISABLED)
        self.okbtn.pack(side=tk.RIGHT)
        self.editor = tk.Entry(editor,width=45)
        self.editor.pack(side=tk.LEFT,expand=True,fill=tk.X)
        self.editor.bind("<Key-Return>",self.ok_click)
        editor.pack(side=tk.BOTTOM,fill=tk.X)
        self.tvw.pack(side=tk.BOTTOM,expand=True,fill=tk.BOTH)

        self.menu=tk.Menu(self.master,tearoff=False)
        self.menu.add_command(label="Open in new window",command=self.open_in_new_window,
                              state=tk.DISABLED)
        self.menu.add_command(label="Add",command=self.new_item,state=tk.DISABLED)
        self.menu.add_command(label="Delete",command=self.del_item,state=tk.DISABLED)
        def on_rightclick(event):
            if len(self.tvw.selection()) <= 1:
                self.tvw.event_generate("<Button-1>",x=event.x,y=event.y) # 选择当前右击的项
            self.menu.post(event.x_root,event.y_root)
        self.tvw.bind("<B3-ButtonRelease>",on_rightclick)
    def load_image(self):
        # 加载images文件夹下的图片
        self.back_image=tk.PhotoImage(master=self.master,
                            file=os.path.join(_IMAGE_PATH,"back.gif"))
        self.forward_image=tk.PhotoImage(master=self.master,
                            file=os.path.join(_IMAGE_PATH,"forward.gif"))
        self.refresh_image=tk.PhotoImage(master=self.master,
                            file=os.path.join(_IMAGE_PATH,"refresh.gif"))
        self.obj_image=tk.PhotoImage(master=self.master,
                            file=os.path.join(_IMAGE_PATH,"python.gif"))
        self.num_image=tk.PhotoImage(master=self.master,
                            file=os.path.join(_IMAGE_PATH,"number.gif"))
        self.str_image=tk.PhotoImage(master=self.master,
                            file=os.path.join(_IMAGE_PATH,"string.gif"))
        self.list_image=tk.PhotoImage(master=self.master,
                            file=os.path.join(_IMAGE_PATH,"list.gif"))
        self.empty_list_image=tk.PhotoImage(master=self.master,
                            file=os.path.join(_IMAGE_PATH,"empty_list.gif"))
        self.tuple_image=tk.PhotoImage(master=self.master,
                            file=os.path.join(_IMAGE_PATH,"tuple.gif"))
        self.empty_tuple_image=tk.PhotoImage(master=self.master,
                            file=os.path.join(_IMAGE_PATH,"empty_tuple.gif"))
        self.dict_image=tk.PhotoImage(master=self.master,
                            file=os.path.join(_IMAGE_PATH,"dict.gif"))
        self.empty_dict_image=tk.PhotoImage(master=self.master,
                            file=os.path.join(_IMAGE_PATH,"empty_dict.gif"))
        self.func_image=tk.PhotoImage(master=self.master,
                            file=os.path.join(_IMAGE_PATH,"function.gif"))
        self.code_image=tk.PhotoImage(master=self.master,
                            file=os.path.join(_IMAGE_PATH,"codeobject.gif"))
    def clear(self):
        # 清除Treeview的数据
        for root in self.tvw.get_children(""): # 获取根项
            for item in self.tvw.get_children(root):
                self.tvw.delete(item)
    def _get_image(self,obj):
        if isinstance(obj,int) or isinstance(obj,float):
            return self.num_image
        elif isinstance(obj,str):
            return self.str_image
        elif isinstance(obj,tuple):
            return self.tuple_image if len(obj) else self.empty_tuple_image
        elif isinstance(obj,list):
            return self.list_image if len(obj) else self.empty_list_image
        elif isdict(obj):
            return self.dict_image if len(obj) else self.empty_dict_image
        elif isfunc(obj):
            return self.func_image
        elif iscode(obj):
            return self.code_image
        else:return self.obj_image
    def _get_type(self,obj):
        if isfunc(obj):
            return self.functions_tag
        elif isinstance(obj,type):
            return self.classes_tag
        else:return self.attributes_tag
    def refresh(self,event=None):
        "更新自身显示的数据。"
        obj=self.obj
        self.master.title("{} - {}".format(self.title,objectname(obj)))
        self.label["text"]=" Path: %s  Object: %s" % (self.name, _shortrepr(obj))
        self.clear()
        max_length = 500 # 避免引发性能问题
        # 添加属性
        attrs=dir(obj)
        for i in range(len(attrs)):
            attr=attrs[i]
            if self.verbose or not attr.startswith("_"):
                try:
                    object=getattr(obj,attr)
                    value=_shortrepr(object,max_length)
                    image=self._get_image(object)
                    self.tvw.insert(self._get_type(object), tk.END, #attr,
                                    text=attr, image=image,
                                    values=(value,)) # values从第二列开始
                except Exception as error: # 显示错误消息
                    value='<{}: {}>'.format(type(error).__name__,str(error))
                    self.tvw.insert(self.attributes_tag, tk.END,
                                    text=attr, image=self.obj_image,
                                    values=(value,),tags=("error",))
        # __bases__属性一般不会出现在dir()的返回值中
        if hasattr(obj,"__bases__") and "__bases__" not in attrs:
            bases=obj.__bases__
            self.tvw.insert(self.classes_tag, tk.END, "__bases__",
                            text="__bases__", image=self._get_image(bases),
                            values=(repr(bases),))
        # 添加列表数据
        if isinstance(obj,(list,tuple)):
            for i in range(len(obj)):
                index=str(i)
                try:
                    object=obj[i]
                    value=_shortrepr(object,max_length)
                    image=self._get_image(object)
                    self.tvw.insert(self.lst_tag, tk.END,
                                    text=index, image=image,
                                    values=(value,))
                except Exception as err:
                    value='<{}!>'.format(type(err).__name__)
                    self.tvw.insert(self.lst_tag, tk.END,
                                    text=index, image=self.obj_image,
                                    values=(value,),tags=("error",))

        # 添加字典数据
        if isdict(obj):
            for key in obj.keys():
                key_name=repr(key)
                try:
                    object=obj[key]
                    value=_shortrepr(object,max_length)
                    image=self._get_image(object)
                    self.tvw.insert(self.dict_tag, tk.END,
                                    text=key_name, image=image,
                                    values=(value,))
                except Exception as err:
                    value='<{}!>'.format(type(err).__name__)
                    self.tvw.insert(self.dict_tag, tk.END,
                                    text=key_name, image=self.obj_image,
                                    values=(value,),tags=("error",))

        self.okbtn['state'] = tk.DISABLED # 由于刷新后不会再选中刷新前的数据
        self.on_select() # 重置菜单的状态 (是否可点击)

    def browse(self,obj,name="obj"):
        "浏览一个新对象(obj)。"
        self.obj=obj # 更新self.obj及名称
        self.name=name
        self.refresh()
    def on_select(self,event=None):
        selection = self.tvw.selection()
        if len(selection) != 1:
            self.okbtn['state'] = tk.DISABLED
            self.menu.entryconfig("Add",state=tk.DISABLED)
            self.editor.delete(0,tk.END)
            if len(selection) > 1:
                self.menu.entryconfig("Open in new window",state=tk.NORMAL)
            else:
                self.menu.entryconfig("Open in new window",state=tk.DISABLED)
            if len(selection) > 0:
                self.menu.entryconfig("Delete",state=tk.NORMAL)
            else:
                self.menu.entryconfig("Delete",state=tk.DISABLED)
        else:
            parent=self.tvw.parent(selection[0])
            if parent:
                #value_str=self.tvw.item(selection[0])["values"][0] # 现已弃用，由于使用了_shortrepr()
                attr=self.tvw.item(selection)["text"]
                if parent==self.dict_tag:
                    value_str=repr(self.obj[eval(attr)])
                elif parent==self.lst_tag:
                    value_str=repr(self.obj[int(attr)])
                else:
                    value_str=repr(getattr(self.obj,attr))
                self.editor.delete(0,tk.END)
                self.editor.insert(0,value_str)
                if parent==self.lst_tag and isinstance(self.obj,tuple):
                    self.okbtn['state'] = tk.DISABLED # 元组的属性不可编辑
                    self.menu.entryconfig("Add",state=tk.DISABLED)
                    self.menu.entryconfig("Delete",state=tk.DISABLED)
                else:
                    self.okbtn['state'] = tk.NORMAL
                    self.menu.entryconfig("Add",state=tk.NORMAL)
                    self.menu.entryconfig("Delete",state=tk.NORMAL)
                self.menu.entryconfig("Open in new window",state=tk.NORMAL)
            else:
                self.okbtn['state'] = tk.DISABLED
                self.editor.delete(0,tk.END)
                if selection[0]==self.lst_tag and not isinstance(self.obj,list) \
                    or selection[0]==self.dict_tag and not isinstance(self.obj,dict):
                    self.menu.entryconfig("Add",state=tk.DISABLED)
                else:self.menu.entryconfig("Add",state=tk.NORMAL)
                self.menu.entryconfig("Open in new window",state=tk.DISABLED)
                self.menu.entryconfig("Delete",state=tk.DISABLED)
    def on_open(self,event=None,new_window=False):
        #当双击Treeview或按回车时, 进一步浏览选中的属性。
        #selection为所有选中项的元组,以('Hxxx',)的形式表示
        for selection in self.tvw.selection():
            parent=self.tvw.parent(selection)
            if not parent:continue # 如果没有父项
            attr=self.tvw.item(selection)["text"]
            if parent==self.dict_tag:
                obj=self.obj[eval(attr)]
                path="%s[%s]" % (self.name,attr)
            elif parent==self.lst_tag:
                obj=self.obj[int(attr)]
                path="%s[%s]" % (self.name,attr)
            else:
                obj=getattr(self.obj,attr)
                path=self.name+"."+attr
            if not (new_window or self.multi_window):
                self.obj=obj
                self.name=path
                self.history=self.history[:self.history_index+1] # 清除后面的数据
                self.history.append((obj,path))
                self.history_index+=1
                self.refresh()
                break # 跳转到新对象后，停止处理其他选中的项
            else:browse(obj,self.verbose,path,mainloop=False, # 在新窗口中浏览
                        multi_window=self.multi_window,refresh_history=self.refresh_history,
                        root_obj=self.root_obj,rootobj_name=self.rootobj_name)
    def open_in_new_window(self):
        self.on_open(new_window=True)
    def ok_click(self,event=None):
        if self.okbtn["state"]==tk.DISABLED:
            return
        selected=self.tvw.selection()[0]
        parent=self.tvw.parent(selected)
        item=self.tvw.item(selected)
        attr=item["text"]
        value=eval(self.editor.get())
        if parent==self.dict_tag:
            self.obj[eval(attr)]=value
        elif parent==self.lst_tag:
            self.obj[int(attr)]=value
        else:
            setattr(self.obj,attr,value)
        self.tvw.item(selected,values=(repr(value),),
                      image=self._get_image(value))
    def new_item(self):
        if not self.tvw.selection():return
        selected=self.tvw.selection()[0]
        if self.dict_tag in (selected,self.tvw.parent(selected)):
            key=simpledialog.askstring("New item","Enter key (use quotes for strings):")
            if not key:return
            value=simpledialog.askstring("New item","Enter value:")
            if not value:return
            self.obj[eval(key)]=eval(value)
        elif self.lst_tag in (selected,self.tvw.parent(selected)):
            index=simpledialog.askstring("New item","Enter index for new item (0, 1, 2, ...):")
            if not index:return
            value=simpledialog.askstring("New item","Enter value:")
            if not value:return
            self.obj.insert(int(index),eval(value))
        else:
            attr=simpledialog.askstring("New item","Enter attribute name (no quotes needed):")
            if not attr:return
            value=simpledialog.askstring("New item","Enter value:")
            if not value:return
            setattr(self.obj,attr,eval(value))
        self.navigate_history()
    def del_item(self,event=None):
        # 删除选中的项
        for selection in self.tvw.selection():
            parent=self.tvw.parent(selection)
            if not parent:continue # 如果没有父项
            attr=self.tvw.item(selection)["text"]
            if parent==self.dict_tag:
                del self.obj[eval(attr)]
            elif parent==self.lst_tag:
                del self.obj[int(attr)]
            else:
                delattr(self.obj,attr)
        self.refresh()
    def navigate_history(self,event=None): # 转到当前的历史记录
        obj,path = self.history[self.history_index]
        if self.refresh_history:
            try:
                # 对象的属性可能有改变，重新获取对象的属性
                scope={self.rootobj_name:self.root_obj} # 获取第一个浏览的根对象及其名称
                object=eval(path,scope)
            except Exception: # 默认使用新获取的对象，只有出错时，才使用旧的对象
                object=obj
        else:object=obj
        self.browse(object,path)
    def back(self): # 后退
        if self.history_index!=0:
            self.history_index-=1
            self.navigate_history()
    def forward(self): # 前进
        if self.history_index!=len(self.history)-1:
            self.history_index+=1
            self.navigate_history()

def browse(object,verbose=True,name="obj",
           mainloop=True,multi_window=False,refresh_history=True,
           root_obj=None,rootobj_name=None):
    """Browse a Python object through a graphical interface.
verbose: Similar to describe, it indicates whether to print special methods \
of the object (e.g., __init__).
name: Specifies the display name of the object.
mainloop: Determines whether the function waits for the window to close before \
exiting, meaning whether the browse function will be blocking.
multi_window: Indicates whether to open a new window when double-clicking \
(or pressing Enter) to browse a new object.
refresh_history: Determines whether to re-fetch the object's \
attributes when navigating backward or forward. If True, editing attributes \
and then navigating will show changes in the object; otherwise, it will not.
root_obj and rootobj_name: Specify the root object and its name (for internal use)."""
    root=tk.Tk()
    if sys.platform == "win32": # 高dpi支持
        dpi_x,dpi_y = get_dpi_scale()
    else:dpi_x = dpi_y = 1
    width, height = 480,400
    root.geometry("%dx%d" % (width*dpi_x,height*dpi_y))
    ObjectBrowser(root,object,verbose,name,multi_window=multi_window,
                  refresh_history=refresh_history,root_obj=root_obj,
                  rootobj_name=rootobj_name)
    if mainloop:root.mainloop()

def test():
    if sys.platform == 'win32': # Windows下的高DPI支持
        ctypes.OleDLL('shcore').SetProcessDpiAwareness(1)
    class Test:
        def __init__(self):
            self.a='foo';self._cnt=0
            self.list=["foo","bar",1]
            self.tuple=("foo","bar",2)
            self.dict={"a":"bar","b":1}
        @property
        def cnt(self):
            self._cnt+=1
            return self._cnt

    browse(Test(),verbose=True)

if __name__=="__main__":test()
