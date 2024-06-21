"以图形方式浏览Python对象的模块。"
import sys,os,types,typing
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as msgbox
import tkinter.simpledialog as simpledialog
from inspect import isfunction,ismethod,isgeneratorfunction,isgenerator,iscode
try: from . import objectname,_shortrepr
# ImportError,SystemError: 修复Python 3.4中的bug
except (ImportError,SystemError):from __init__ import objectname,_shortrepr

_IMAGE_PATH=(os.path.split(__file__)[0]+"\\images")

def isfunc(obj):
    # 判断一个对象是否为函数或方法
    if isfunction(obj) or ismethod(obj):return True
    # 使用typing而不用types.WrapperDescriptorType是为了与旧版本兼容
    func_types=[types.LambdaType,types.BuiltinFunctionType,
                types.BuiltinMethodType,typing.WrapperDescriptorType,
                typing.MethodWrapperType,typing.MethodDescriptorType]
    if sys.version_info.minor>=7: # Python 3.7及以上
        func_types.append(types.ClassMethodDescriptorType)
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
class ScrolledTreeview(ttk.Treeview):
    "可滚动的Treeview控件,继承自ttk.Treeview。"
    def __init__(self,master,**options):
        self.frame=tk.Frame(master)
        ttk.Treeview.__init__(self,self.frame,**options)
        
        self.hscroll=ttk.Scrollbar(self.frame,orient=tk.HORIZONTAL,
                                   command=self.xview)
        self.vscroll=ttk.Scrollbar(self.frame,command=self.yview)
        self["yscrollcommand"]=self.vscroll.set
        self.vscroll.pack(side=tk.RIGHT,fill=tk.Y)
        ttk.Treeview.pack(self,side=tk.BOTTOM,expand=True,fill=tk.BOTH)     
    def pack(self,**options):
        self.frame.pack(**options)
    def grid(self,**options):
        self.frame.grid(**options)
    def place(self,**options):
        self.frame.place(**options)

class ObjectBrowser():
    title="Python对象浏览器"
    obj_image=None
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
            self.master.iconbitmap(_IMAGE_PATH+r"\python.ico")
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
        self.tvw.heading("#0",text="属性/索引/键")
        self.tvw.heading("#1",text="值")
        self.tvw.column("#0", stretch=0) # 不允许拉伸
        self.tvw.column("#1", stretch=1)
        self.tvw.bind("<<TreeviewSelect>>",self.on_select)
        self.tvw.bind("<Double-Button-1>",self.on_open)
        self.tvw.bind("<Key-Return>",self.on_open)
        self.tvw.bind("<Key-Delete>",self.del_item)
        self.tvw.tag_configure("error",foreground="red") # 经测试, Python 3.7-3.9中无法显示颜色效果(bug?)
        self.master.bind("<F5>",self.navigate_history) #refresh)

        self.functions_tag=self.tvw.insert('',index=0,text="函数、方法")
        self.attributes_tag=self.tvw.insert('',index=1,text="属性")
        self.classes_tag=self.tvw.insert('',index=2,text="类")
        self.lst_tag=self.tvw.insert('',index=3,text="列表数据")
        self.dict_tag=self.tvw.insert('',index=4,text="字典数据")
        editor = ttk.Labelframe(self.master, text='编辑值',
                                width=100, height=100)
        self.okbtn=ttk.Button(editor,text="确定",
                              command=self.ok_click,state=tk.DISABLED)
        self.okbtn.pack(side=tk.RIGHT)
        self.editor = tk.Entry(editor,width=45)
        self.editor.pack(side=tk.LEFT,expand=True,fill=tk.X)
        self.editor.bind("<Key-Return>",self.ok_click)
        editor.pack(side=tk.BOTTOM,fill=tk.X)
        self.tvw.pack(side=tk.BOTTOM,expand=True,fill=tk.BOTH)

        self.menu=tk.Menu(self.master,tearoff=False)
        self.menu.add_command(label="新增",command=self.new_item,state=tk.DISABLED)
        self.menu.add_command(label="删除",command=self.del_item,state=tk.DISABLED)
        self.tvw.bind("<Button-3>",lambda event:self.menu.post(event.x_root,event.y_root))
    def load_image(self):
        # 加载images文件夹下的图片
        self.back_image=tk.PhotoImage(master=self.master,
                                     file=_IMAGE_PATH+r"\back.gif")
        self.forward_image=tk.PhotoImage(master=self.master,
                                     file=_IMAGE_PATH+r"\forward.gif")
        self.refresh_image=tk.PhotoImage(master=self.master,
                                     file=_IMAGE_PATH+r"\refresh.gif")
        self.obj_image=tk.PhotoImage(master=self.master,
                                     file=_IMAGE_PATH+r"\python.gif")
        self.num_image=tk.PhotoImage(master=self.master,
                                     file=_IMAGE_PATH+r"\number.gif")
        self.str_image=tk.PhotoImage(master=self.master,
                                     file=_IMAGE_PATH+r"\string.gif")
        self.list_image=tk.PhotoImage(master=self.master,
                                     file=_IMAGE_PATH+r"\list.gif")
        self.empty_list_image=tk.PhotoImage(master=self.master,
                                     file=_IMAGE_PATH+r"\empty_list.gif")
        self.tuple_image=tk.PhotoImage(master=self.master,
                                     file=_IMAGE_PATH+r"\tuple.gif")
        self.empty_tuple_image=tk.PhotoImage(master=self.master,
                                     file=_IMAGE_PATH+r"\empty_tuple.gif")
        self.dict_image=tk.PhotoImage(master=self.master,
                                     file=_IMAGE_PATH+r"\dict.gif")
        self.empty_dict_image=tk.PhotoImage(master=self.master,
                                     file=_IMAGE_PATH+r"\empty_dict.gif")
        self.func_image=tk.PhotoImage(master=self.master,
                                     file=_IMAGE_PATH+r"\function.gif")
        self.code_image=tk.PhotoImage(master=self.master,
                                     file=_IMAGE_PATH+r"\codeobject.gif")
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
        self.label["text"]=" 路径: %s 对象: %s" % (self.name, repr(obj))
        self.clear()
        # 添加属性
        attrs=dir(obj)
        for i in range(len(attrs)):
            attr=attrs[i]
            if self.verbose or not attr.startswith("_"):
                try:
                    object=getattr(obj,attr)
                    value=_shortrepr(object)
                    image=self._get_image(object)
                    self.tvw.insert(self._get_type(object), tk.END, #attr,
                                    text=attr, image=image,
                                    values=(value,)) # values从第二列开始
                except Exception as error: # 显示错误消息
                    value='<{}!>'.format(type(error).__name__)
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
        if isinstance(obj,list) or isinstance(obj,tuple):
            for i in range(len(obj)):
                index=str(i)
                try:
                    object=obj[i]
                    value=_shortrepr(object)
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
                    value=_shortrepr(object)
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
                
    def browse(self,obj,name="obj"):
        "浏览一个新对象(obj)。"
        self.obj=obj # 更新self.obj及名称
        self.name=name
        self.refresh()
    def on_select(self,event):
        selection = self.tvw.selection()
        if len(selection) != 1:
            self.okbtn['state'] = tk.DISABLED
            self.menu.entryconfig("新增",state=tk.DISABLED)
            self.menu.entryconfig("删除",state=tk.NORMAL)
            self.editor.delete(0,tk.END)
        else:
            parent=self.tvw.parent(selection[0])
            if parent:
                value_str=self.tvw.item(selection[0])["values"][0]
                self.editor.delete(0,tk.END)
                self.editor.insert(0,value_str)
                if parent==self.lst_tag and isinstance(self.obj,tuple):
                    self.okbtn['state'] = tk.DISABLED # 元组的属性不可编辑
                    self.menu.entryconfig("删除",state=tk.DISABLED)
                else:
                    self.okbtn['state'] = tk.NORMAL
                    self.menu.entryconfig("删除",state=tk.NORMAL)
                self.menu.entryconfig("新增",state=tk.DISABLED)
            else:
                self.okbtn['state'] = tk.DISABLED
                self.editor.delete(0,tk.END)
                if selection[0]==self.lst_tag and not isinstance(self.obj,list) \
                    or selection[0]==self.dict_tag and not isinstance(self.obj,dict):
                    self.menu.entryconfig("新增",state=tk.DISABLED)
                else:self.menu.entryconfig("新增",state=tk.NORMAL)
                self.menu.entryconfig("删除",state=tk.DISABLED)
    def on_open(self,event):
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
            if not self.multi_window:
                self.obj=obj
                self.name=path
                self.history=self.history[:self.history_index+1] # 清除后面的数据
                self.history.append((obj,path))
                self.history_index+=1
                self.refresh()
                break # 停止处理其他选中的项
            else:browse(obj,self.verbose,path,mainloop=False, # 在新窗口中浏览
                        multi_window=self.multi_window,refresh_history=self.refresh_history,
                        root_obj=self.root_obj,rootobj_name=self.rootobj_name)
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
        if selected==self.dict_tag:
            key=simpledialog.askstring("新增","输入字典键 (如果为字符串，需要加引号):")
            if not key:return
            value=simpledialog.askstring("新增","输入值:")
            if not value:return
            self.obj[eval(key)]=eval(value)
        elif selected==self.lst_tag:
            index=simpledialog.askstring("新增","输入新增列表项的索引 (0,1,2,...):")
            if not index:return
            value=simpledialog.askstring("新增","输入值:")
            if not value:return
            self.obj.insert(int(index),eval(value))
        else:
            attr=simpledialog.askstring("新增","输入属性名称 (无需引号):")
            if not attr:return
            value=simpledialog.askstring("新增","输入值:")
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
            except Exception:
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

def browse(object,verbose=False,name="obj",
           mainloop=True,multi_window=False,refresh_history=True,
           root_obj=None,rootobj_name=None):
    """以图形界面浏览一个Python对象。
verbose:与describe相同,是否打印出对象的特殊方法(如__init__)。
name:指定对象显示的名称。
mainloop:是否等待窗口关闭后才退出函数，也就是browse函数是否会被阻塞。
multi_window:双击(或按Enter)来浏览新对象时是否打开新窗口。
refresh_history:后退或前进时，是否重新获取对象的属性。
如果为True，编辑了属性再后退或前进，浏览到的对象就会变化，反之则不会。
root_obj和rootobj_name:指定根对象及其名称(主要由内部使用)。"""
    root=tk.Tk()
    root.geometry("480x400")
    ObjectBrowser(root,object,verbose,name,multi_window=multi_window,
                  refresh_history=refresh_history,root_obj=root_obj,
                  rootobj_name=rootobj_name)
    if mainloop:root.mainloop()

def test():
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
