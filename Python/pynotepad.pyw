"""简介 Introduction:
An open-source text editor written in Python.
It supports editing text files,binary files with various encodings
which can be automatically detected.
When you edit a binary file, the contents of the file are displayed as escape sequences.
You can find and replace words.You're also able to choose themes you prefer.
In addition, code highlighting is supported when editing Python code files,like IDLE.
What's more, dragging and dropping files into the editor window is now supported.

一款使用tkinter编写的文本编辑器, 支持编辑文本文件、二进制文件、自由选择主题。
支持ansi、gbk、utf-8等编码, 以及调用chardet库自动检测编码。
编辑二进制文件时, 文件内容以转义序列形式显示。
支持查找、替换; 且支持撤销、重做; 支持将文件拖放入窗口。
可自由选择主题和字体, 改变字体大小。
编辑python代码文件时, 支持代码高亮显示, 类似IDLE。

作者:qfcy (七分诚意)
版本:%s
"""
import sys,os,pickle
from tkinter import *
from tkinter.scrolledtext import ScrolledText
import tkinter.ttk as ttk
import tkinter.messagebox as msgbox
import tkinter.filedialog as filediag
import tkinter.simpledialog as simpledialog
from tkinter.colorchooser import askcolor
from tkinter import font

# 以下为可选(非必需)的模块
import webbrowser
try:
    from idlelib.colorizer import ColorDelegator
    from idlelib.percolator import Percolator
except ImportError:
    ColorDelegator=Percolator=None
try:import windnd
except ImportError:windnd=None
try:import chardet
except ImportError:chardet=None

__email__="3076711200@qq.com"
__author__="qfcy qq:3076711200"
__version__="1.3.5";__doc__=__doc__%__version__ # 在__doc__中加入版本信息

def view_hex(byte):
    result=''
    if hasattr(bytes,'hex'):
        conv_hex = bytes.hex
    else: # 低于Python 3.5(如3.4版), 没有bytes.hex内置方法
        conv_hex = lambda b:hex(int.from_bytes(b,'big'))[2:]\
                           .zfill(len(b)*2)
    for i in range(0,len(byte)):
        result+= conv_hex(byte[i:i+1]).zfill(2) + ' '
        if (i+1) % 4 == 0:result+='\n'
    return result

def to_escape_str(byte,linesep=True):
    # 将字节(bytes)转换为转义字符串
    # linesep: 是否以length间隔加入换行符, 加入换行符可提高Text控件的显示速度
    str='';length=1024
    for i in range(0,len(byte),length):
        str+=repr( byte[i: i+length] ) [2:-1]
        if linesep:str+='\n'
    return str

def to_bytes(escape_str):
    # 将转义字符串转换为字节
    # -*****- 1.2.5版更新: 忽略二进制模式中文字的换行符
    escape_str=escape_str.replace('\n','')
    escape_str=escape_str.replace('"""','\\"\\"\\"') # 避免引号导致的SyntaxError
    escape_str=escape_str.replace("'''","\\'\\'\\'")
    try:
        return eval('b"""'+escape_str+'"""')
    except SyntaxError:
        return eval("b'''"+escape_str+"'''")

def bell_(widget=None):
    try:
        import winsound
        winsound.PlaySound('.',winsound.SND_ASYNC)
    except (ImportError, RuntimeError):
        if widget is not None:widget.bell()

def handle(err,parent=None):
    # showinfo()中,parent参数指定消息框的父窗口
    msgbox.showinfo("错误",type(err).__name__+': '+str(err),parent=parent)

class SearchDialog(Toplevel):
    #查找对话框
    def __init__(self,master):
        self.master=master
        self.coding=self.master.coding.get()
    def init_window(self,title="查找"):
        Toplevel.__init__(self,self.master)
        self.title(title)
        if sys.platform=="win32":
            self.attributes("-toolwindow",True)
        self.attributes("-topmost",True)
        # 当父窗口隐藏后，窗口也跟随父窗口隐藏
        self.transient(self.master)
        self.wm_protocol("WM_DELETE_WINDOW",self.onquit)
    def show(self):
        self.init_window()
        frame=Frame(self)
        ttk.Button(frame,text="查找下一个",command=self.search).pack()
        ttk.Button(frame,text="退出",command=self.onquit).pack()
        frame.pack(side=RIGHT,fill=Y)
        inputbox=Frame(self)
        Label(inputbox,text="查找内容:").pack(side=LEFT)
        self.keyword=StringVar(self.master)
        keyword=ttk.Entry(inputbox,textvariable=self.keyword)
        keyword.pack(side=LEFT,expand=True,fill=X)
        keyword.bind("<Key-Return>",self.search)
        keyword.focus_force()
        inputbox.pack(fill=X)
        options=Frame(self)
        self.create_options(options)
        options.pack(fill=X)
    def create_options(self,master):
        Label(master,text="选项: ").pack(side=LEFT)
        self.use_regexpr=IntVar(self.master)
        ttk.Checkbutton(master,text="使用正则表达式",variable=self.use_regexpr)\
        .pack(side=LEFT)
        self.match_case=IntVar(self.master)
        ttk.Checkbutton(master,text="区分大小写",variable=self.match_case)\
        .pack(side=LEFT)
        self.use_escape_char=IntVar(self.master)
        self.use_escape_char.set(self.master.isbinary)
        ttk.Checkbutton(master,text="使用转义字符",variable=self.use_escape_char)\
        .pack(side=LEFT)

    def search(self,event=None,mark=True,bell=True):
        text=self.master.contents
        key=self.keyword.get()
        if not key:return
        # 验证用户输入是否正常
        if self.use_escape_char.get():
            try:key=str(to_bytes(key),encoding=self.coding)
            except Exception as err:
                handle(err,parent=self);return
        if self.use_regexpr.get():
            try:re.compile(key)
            except re.error as err:
                handle(err,parent=self);return
        # 默认从当前光标位置开始查找
        pos=text.search(key,INSERT,'end-1c',# end-1c:忽略末尾换行符
                        regexp=self.use_regexpr.get(),
                        nocase=not self.match_case.get())
        if not pos:
            # 尝试从开头循环查找
            pos=text.search(key,'1.0','end-1c',
                        regexp=self.use_regexpr.get(),
                        nocase=not self.match_case.get())
        if pos:
            if self.use_regexpr.get(): # 获取正则表达式匹配的字符串长度
                text_after = text.get(pos,END)
                flag = re.IGNORECASE if not self.match_case.get() else 0
                length = re.match(key,text_after,flag).span()[1]
            else:
                length = len(key)
            newpos="%s+%dc"%(pos,length)
            text.mark_set(INSERT,newpos)
            if mark:self.mark_text(pos,newpos)
            return pos,newpos
        elif bell: # 未找到,返回None
            bell_(widget=self)
    def findnext(self,cursor_pos='end',mark=True,bell=True):
        # cursor_pos:标记文本后将光标放在找到文本开头还是末尾
        # 因为search()默认从当前光标位置开始查找
        # end 用于查找下一个操作, start 用于替换操作
        result=self.search(mark=mark,bell=bell)
        if not result:return
        if cursor_pos=='end':
            self.master.contents.mark_set('insert',result[1])
        elif cursor_pos=='start':
            self.master.contents.mark_set('insert',result[0])
        return result
    def mark_text(self,start_pos,end_pos):
        text=self.master.contents
        text.tag_remove("sel","1.0",END) # 移除旧的tag
        # 已知问题: 代码高亮显示时, 无法突出显示找到的文字
        text.tag_add("sel", start_pos,end_pos) # 添加新的tag "sel"
        lines=text.get('1.0',END)[:-1].count(os.linesep) + 1
        lineno=int(start_pos.split('.')[0])
        # 滚动文本框, 使被找到的内容显示 ( 由于只判断行数, 已知有bug)
        text.yview('moveto', str((lineno-text['height'])/lines)) # -****- 1.2.5版
        text.focus_force()
        self.master.update_status()
    def onquit(self):
        self.withdraw()

class ReplaceDialog(SearchDialog):
    #替换对话框
    def show(self):
        self.init_window(title="替换")
        frame=Frame(self)
        ttk.Button(frame,text="查找下一个", command=self._findnext).pack()
        ttk.Button(frame,text="替换", command=self.replace).pack()
        ttk.Button(frame,text="全部替换", command=self.replace_all).pack()
        ttk.Button(frame,text="退出", command=self.onquit).pack()
        frame.pack(side=RIGHT,fill=Y)

        inputbox=Frame(self)
        Label(inputbox,text="查找内容:").pack(side=LEFT)
        self.keyword=StringVar(self.master)
        keyword=ttk.Entry(inputbox,textvariable=self.keyword)
        keyword.pack(side=LEFT,expand=True,fill=X)
        keyword.focus_force()
        inputbox.pack(fill=X)

        replace=Frame(self)
        Label(replace,text="替换为:  ").pack(side=LEFT)
        self.text_to_replace=StringVar(self.master)
        replace_text=ttk.Entry(replace,textvariable=self.text_to_replace)
        replace_text.pack(side=LEFT,expand=True,fill=X)
        replace_text.bind("<Key-Return>",self.replace)
        replace.pack(fill=X)

        options=Frame(self)
        self.create_options(options)
        options.pack(fill=X)
    def _findnext(self):# 仅用于"查找下一个"按钮功能
        text=self.master.contents
        sel_range=text.tag_ranges('sel') # 获得选区的起点和终点
        if sel_range:
            selectarea = sel_range[0].string, sel_range[1].string
            result = self.findnext('start')
            if result is None:return
            if result[0] == selectarea[0]: # 若仍停留在原位置
                text.mark_set('insert',result[1])# 从选区终点继续查找
                self.findnext('start')
        else:
            self.findnext('start')
    def replace(self,bell=True,mark=True):
        text=self.master.contents
        result=self.search(mark=False,bell=bell)
        if not result:return # 标志已无文本可替换
        self.master.text_change()
        pos,newpos=result
        newtext=self.text_to_replace.get()
        try:
            if self.use_escape_char.get():
                newtext=to_bytes(newtext).decode(self.master.coding.get())
            if self.use_regexpr.get():
                old=text.get(pos,newpos)
                newtext=re.sub(self.keyword.get(),newtext,old)
        except Exception as err:
            handle(err,parent=self);return
        text.delete(pos,newpos)
        text.insert(pos,newtext)
        end_pos="%s+%dc"%(pos,len(newtext))
        if mark:self.mark_text(pos,end_pos)
        return pos,end_pos
    def replace_all(self):
        self.master.contents.mark_set("insert","1.0")
        flag=False # 标志是否已有文字被替换

        # 以下代码会导致无限替换, 使程序卡死, 新的代码修复了该bug
        #while self.replace(bell=False)!=-1:
        #    flag=True
        last = (0,0)
        while True:
            result=self.replace(bell=False,mark=False)
            if result is None:break
            flag = True
            result = self.findnext('start',bell=False,mark=False)
            if result is None:return
            ln,col = result[0].split('.')
            ln = int(ln);col = int(col)
            # 判断新的偏移量是增加还是减小
            if ln < last[0] or (ln==last[0] and col<last[1]):
                self.mark_text(*result) # 已完成一轮替换
                break
            last=ln,col
        if not flag:bell_()

class Editor(Tk):
    TITLE="PyNotepad"
    encodings="ansi","utf-8","utf-16","utf-32","gbk","big5"
    # 判断是否有chardet库, 有就启用"自动"功能
    if chardet is not None:encodings=("自动",)+encodings
    ICON="notepad.ico"
    NORMAL_CODING="自动" if chardet is not None else "utf-8"
    FONTSIZES=8, 9, 10, 11, 12, 14, 16, 18, 20, 24, 36, 48
    NORMAL_FONT='宋体'
    NORMAL_FONTSIZE=11
    if sys.platform=="win32":
    	TEXT_BG="SystemWindow";TEXT_FG="SystemWindowText" # 系统默认颜色
    	CONFIGFILE=os.path.join(os.getenv("userprofile"),".pynotepad.pkl")
    else:
    	TEXT_BG="white";TEXT_FG="black" # TODO:获取其他系统的默认颜色
    	CONFIGFILE=os.path.join(os.getenv("HOME"),".pynotepad.pkl")
    FILETYPES=[("所有文件","*.*")]
    AUTOWRAP=CHAR
    SHOW_STATUS=True

    instances=[]
    def __init__(self,filename=""):
        super().__init__()
        self.withdraw() # 暂时隐藏窗口,避免调用create_widgets()时窗口闪烁
        self.title(self.TITLE) # 初始化时预先显示标题
        self.bind("<Key>",self.window_onkey)
        self.protocol("WM_DELETE_WINDOW",self.ask_for_save)

        self.isbinary=self.file_modified=False
        self.colorobj=self._codefilter=None
        self._dialogs={}
        Editor.instances.append(self)

        self.load_icon()
        self.loadconfig()
        self.create_widgets()
        self.wm_deiconify();self.update() # wm_deiconfy恢复被隐藏的窗口
        if windnd:windnd.hook_dropfiles(self,func=self.onfiledrag);self.drag_files=[]
        self.filename=''
        if filename:
            self.load(filename)
        else:self.change_title() # 更改标题
    def load_icon(self):
        for path in sys.path + [os.path.split(sys.executable)[0]]: # 用于Py2exe
            try:
                self.iconbitmap("{}\\{}".format(path,self.ICON))
            except TclError:pass
            else:break
    def create_widgets(self):
        # 创建控件
        self.statusbar=Frame(self)
        if self.SHOW_STATUS:
            self.statusbar.pack(side=BOTTOM,fill=X)
        self.status=Label(self.statusbar,justify=RIGHT)
        self.status.pack(side=RIGHT)
        self.txt_decoded=ScrolledText(self.statusbar,
                        bg=self.TEXT_BG,fg=self.TEXT_FG,width=6,height=6)
        self.txt_decoded.insert('1.0',"在这里查看和编辑解码的数据")
        self.hexdata=ScrolledText(self.statusbar,
                        bg=self.TEXT_BG,fg=self.TEXT_FG,width=14,height=5)
        self.hexdata.insert('1.0',"在这里查看hex十六进制值")

        frame=Frame(self)
        frame.pack(side=TOP,fill=X)

        ttk.Button(frame,text='新建', command=self.new,width=7).pack(side=LEFT)
        ttk.Button(frame,text='打开', command=self.open,width=7).pack(side=LEFT)
        ttk.Button(frame,text='打开二进制文件',
                   command=self.open_as_binary,width=13).pack(side=LEFT)
        ttk.Button(frame,text='保存', command=self.save,width=7).pack(side=LEFT)

        Label(frame,text="编码:").pack(side=LEFT)
        self.coding=StringVar(self)
        self.coding.set(self.NORMAL_CODING)
        coding=ttk.Combobox(frame,textvariable=self.coding)
        def tip(event):
            self.msg['text']='重新打开或保存即可生效'
            self.msg.after(2500,clear)
        def clear():self.msg['text']=''
        coding.bind('<<ComboboxSelected>>',tip)
        coding["value"]=self.encodings
        coding.pack(side=LEFT)
        self.msg=Label(frame)
        self.msg.pack(side=LEFT)

        self.contents=ScrolledText(self,undo=True, width=75, height=24,
                        font = (self.NORMAL_FONT,self.NORMAL_FONTSIZE,"normal"),
                        wrap=self.AUTOWRAP, bg=self.TEXT_BG,fg=self.TEXT_FG)
        self.contents.pack(expand=True,fill=BOTH)
        self.contents.bind("<Key>",self.text_change)
        self.contents.bind("<B1-ButtonRelease>",self.update_status)
        order = self.contents.bindtags() # 修复无法获取选定的文本的bug
        self.contents.bindtags((order[1], order[0])+order[2:])
        self.update_offset()

        self.create_menu()
    def create_binarytools(self):
        if self.isbinary:
            self.txt_decoded.pack(side=LEFT,expand=True,fill=BOTH)
            self.hexdata.pack(fill=Y)
            self.status.pack_forget()
            self.status.pack(fill=X)
            self.editmenu.entryconfig(8,state=NORMAL) # 允许插入十六进制数据
        else: # 隐藏工具
            if self.txt_decoded:
                self.txt_decoded.pack_forget()
            if self.hexdata:
                self.hexdata.pack_forget()
            self.status.pack(side=RIGHT)
            self.editmenu.entryconfig(8,state=DISABLED) # 禁止插入
    def create_menu(self):
        menu=Menu(self)
        filemenu=Menu(self,tearoff=False)
        filemenu.add_command(label="新建",
                             command=self.new,accelerator="Ctrl+N")
        filemenu.add_command(label="新建二进制文件",command=self.new_binary)
        filemenu.add_command(label="打开",
                             command=self.open,accelerator="Ctrl+O")
        filemenu.add_command(label="打开二进制文件",command=self.open_as_binary)
        filemenu.add_command(label="保存",
                             command=self.save,accelerator="Ctrl+S")
        filemenu.add_command(label="另存为",command=self.save_as)
        filemenu.add_separator()
        filemenu.add_command(label="退出",command=self.ask_for_save)

        self.editmenu=Menu(self.contents,tearoff=False)
        master = self.contents
        self.editmenu.add_command(label="剪切  ",
                         command=lambda:self.text_change()\
                                ==master.event_generate("<<Cut>>"))
        self.editmenu.add_command(label="复制  ",
                         command=lambda:master.event_generate("<<Copy>>"))
        self.editmenu.add_command(label="粘贴  ",
                         command=lambda:self.text_change()\
                                ==master.event_generate("<<Paste>>"))
        self.editmenu.add_separator()
        self.editmenu.add_command(label="查找",accelerator="Ctrl+F",
                                  command=lambda:self.show_dialog(SearchDialog))
        self.editmenu.add_command(label="查找下一个",accelerator="F3",
                                  command=self.findnext)
        self.editmenu.add_command(label="替换",accelerator="Ctrl+H",
                                  command=lambda:self.show_dialog(ReplaceDialog))
        self.editmenu.add_separator()
        self.editmenu.add_command(label="插入十六进制数据",state=DISABLED,
                                  command=self.insert_hex)

        view=Menu(self.contents,tearoff=False)
        self.is_autowrap=IntVar(self.contents) # 是否自动换行
        self.is_autowrap.set(1 if self.AUTOWRAP!=NONE else 0)
        view.add_checkbutton(label="自动换行", command=self.set_wrap,
                             variable=self.is_autowrap)
        fontsize=Menu(self.contents,tearoff=False)
        fontsize.add_command(label="选择字体",
                             command=self.choose_font)
        fontsize.add_separator()
        fontsize.add_command(label="增大字体   ",accelerator='Ctrl+ "+"',
                             command=self.increase_font)
        fontsize.add_command(label="减小字体   ",accelerator='Ctrl+ "-"',
                             command=self.decrease_font)
        fontsize.add_separator()

        for i in range(len(self.FONTSIZES)):
            def resize(index=i):
                self.set_fontsize(index)
            fontsize.add_command(label=self.FONTSIZES[i],command=resize)

        self.contents.bind("<Button-3>",
                    lambda event:self.editmenu.post(event.x_root,event.y_root))
        view.add_cascade(label="字体",menu=fontsize)
        theme_menu=Menu(self,tearoff=False)
        theme_menu.add_command(label="选择前景色",command=self.select_fg)
        theme_menu.add_command(label="选择背景色",command=self.select_bg)
        theme_menu.add_command(label="重置",command=self.reset_theme)
        view.add_cascade(label="主题",menu=theme_menu)
        self._show_status=IntVar(self)
        self._show_status.set(1 if self.SHOW_STATUS else 0)
        view.add_checkbutton(label="显示状态栏",command=self.show_statusbar,
                         variable=self._show_status)

        helpmenu=Menu(self,tearoff=False)
        helpmenu.add_command(label="关于",command=self.about)
        helpmenu.add_command(label="反馈",command=self.feedback)

        menu.add_cascade(label="文件",menu=filemenu)
        menu.add_cascade(label="编辑",menu=self.editmenu)
        menu.add_cascade(label="查看",menu=view)
        menu.add_cascade(label="帮助",menu=helpmenu)

        # 创建弹出在self.txt_decoded和self.hexdata的菜单
        popup1=Menu(self.txt_decoded,tearoff=False)
        def _cut():
            self.txt_decoded.event_generate("<<Cut>>")
            self._edit_decoded_event()
        def _paste():
            self.txt_decoded.event_generate("<<Paste>>")
            self._edit_decoded_event()
        popup1.add_command(label="剪切",command=_cut)
        popup1.add_command(
            label="复制",command=lambda:self.txt_decoded.event_generate("<<Copy>>"))
        popup1.add_command(label="粘贴",command=_paste)

        popup2=Menu(self.hexdata,tearoff=False)
        popup2.add_command(
            label="复制",command=lambda:self.hexdata.event_generate("<<Copy>>"))

        self.txt_decoded.bind("<Button-3>",
                    lambda event:popup1.post(event.x_root,event.y_root))
        self.txt_decoded.bind("<Key>",self._edit_decoded_event)
        self.hexdata.bind("<Button-3>",
                    lambda event:popup2.post(event.x_root,event.y_root))

        # 显示菜单
        self.config(menu=menu)

    def show_dialog(self,dialog_type):
        # dialog_type是对话框的类型
        if dialog_type in self._dialogs:
            # 不再显示新的对话框
            d=self._dialogs[dialog_type]
            d.state('normal') # 恢复隐藏的窗口
            d.focus_force()
        else:
            d = dialog_type(self);d.show()
            self._dialogs[dialog_type] = d
    def findnext(self):
        fd = self._dialogs.get(SearchDialog,None)
        if fd:
            if fd.findnext():return
        rd = self._dialogs.get(ReplaceDialog,None)
        if rd:
            rd.findnext()
    def _get_fontname(self):
        font=' '.join(self.contents["font"].split(' ')[:-2])
        # tkinter会将带空格的字体名称用{}括起来
        if '{' in font:
            font = font[1:-1]
        return font
    def set_fontsize(self,index):
        newsize=self.FONTSIZES[index]
        fontname = self._get_fontname()
        self.contents["font"]=(fontname,newsize,"normal")
    def choose_font(self):
        def ok():
            self.contents["font"]=[opt.get()] + \
                                   self.contents["font"].split(' ')[-2:] # 保留原先大小、样式
            dialog.destroy()
        dialog = Toplevel(self)
        dialog.title('选择字体')
        dialog.resizable(False,False)
        dialog.attributes('-toolwindow',True)
        opt = ttk.Combobox(dialog)
        # tkinter.font.families() 获取所有字体名称, 注意root参数
        opt['values']=sorted(font.families(root=self))
        opt.grid(row=0,column=0,columnspan=2,padx=15,pady=20)
        ttk.Button(dialog,text='确定',command=ok).grid(row=1,column=0)
        ttk.Button(dialog,text='取消',command=dialog.destroy).grid(row=1,column=1)
        oldfont = self._get_fontname()
        opt.set(oldfont)
        dialog.grab_set() # 对话框打开时, 不允许用户操作主窗口
        dialog.focus_force()
    def increase_font(self):
        # 增大字体
        fontsize=int(self.contents["font"].split(' ')[-2]) # 使用-2代替1
        index=self.FONTSIZES.index(fontsize)+1
        if 0<=index<len(self.FONTSIZES): self.set_fontsize(index)
    def decrease_font(self):
        # 减小字体
        fontsize=int(self.contents["font"].split(' ')[-2])
        index=self.FONTSIZES.index(fontsize)-1
        if 0<=index<len(self.FONTSIZES): self.set_fontsize(index)
    def set_wrap(self):
        if self.is_autowrap.get():
            self.contents['wrap'] = CHAR
        else:
            self.contents['wrap'] = NONE
        # 注意:由于tkinter会自动设置菜单复选框的变量, 所以不需要此行代码
##        self.is_autowrap.set(int(not self.is_autowrap.get()))
    def select_fg(self):
        self.contents["fg"]=self.txt_decoded["fg"]\
                    =self.hexdata["fg"] = askcolor(parent=self,
                                                   color=self.contents["fg"])[1]
    def select_bg(self):
        self.contents["bg"]=self.txt_decoded["bg"]\
                    =self.hexdata["bg"] = askcolor(parent=self,
                                                   color=self.contents["bg"])[1]
        self.set_tag_bg()
    def reset_theme(self):
        self.contents["bg"]=self.txt_decoded["bg"]\
                    =self.hexdata["bg"] = self.TEXT_BG
        self.contents["fg"]=self.txt_decoded["fg"]\
                    =self.hexdata["fg"] = self.TEXT_FG
        self.set_tag_bg()
    def set_tag_bg(self): # 在代码高亮中, 设置tag的背景色, 使其与文本框背景色匹配
        for tag in self.contents.tag_names():
            if tag.lower() != "sel":
                self.contents.tag_config(tag, background=self.contents["bg"])

    def show_statusbar(self):
        if self._show_status.get():
            if self.isbinary:
                self.statusbar.pack(side=BOTTOM,fill=X)
            else:
                self.statusbar.pack(side=BOTTOM,fill=X)
        else:
            self.statusbar.pack_forget()


    def window_onkey(self,event):
        # 如果按下Ctrl键
        if event.state in (4,6,12,14,36,38,44,46): # 适应多种按键情况(Num,Caps,Scroll)
            key=event.keysym.lower()
            if key=='o':#按下Ctrl+O键
                self.open()
            elif key=='s':#Ctrl+S键
                self.save()
            elif key=='n':
                self.new()
            elif key=='f':
                self.show_dialog(SearchDialog)
            elif key=='h':
                self.show_dialog(ReplaceDialog)
            elif key=='equal':#Ctrl+ "+" 增大字体
                self.increase_font()
            elif key=='minus':#Ctrl+ "-" 减小字体
                self.decrease_font()
        elif event.keysym.lower()=='f3':
            self.findnext()
        elif event.keycode == 93: # 按下了菜单键
            self.editmenu.post(self.winfo_x()+self.winfo_width(),
                               self.winfo_y()+self.winfo_height())

    def text_change(self,event=None):
        self.file_modified=True
        self.update_status();self.change_title()
    def update_status(self,event=None):
        if not self._show_status.get():return
        if self.isbinary:
            try:
                selected=self.contents.get(SEL_FIRST,SEL_LAST)
                raw=to_bytes(selected)
                coding=self.coding.get()
                # 调用chardet库
                if coding=="自动":
                    coding=chardet.detect(raw[:100000])['encoding']
                    if coding is None:coding='utf-8'
                try:text=str(raw,encoding=coding,
                             errors="backslashreplace")
                except TypeError:
                    # 忽略Python 3.4的bug: don't know how to handle
                    # UnicodeDecodeError in error callback
                    text=str(raw,encoding=coding,
                             errors="replace")
                except LookupError as err: # 未知编码
                    handle(err,parent=self);return
                self.txt_decoded.delete("1.0",END)
                self.txt_decoded.insert(INSERT,text)
                self.hexdata.delete("1.0",END)
                self.hexdata.insert(INSERT,view_hex(raw))
                self.status["text"]="选区长度: %d (Bytes)"%len(raw)
            except (TclError,SyntaxError): #忽略未选取内容, 或格式不正确
                self.txt_decoded.delete("1.0",END)
                self.hexdata.delete("1.0",END)
                self.update_offset()
        else:self.update_offset()
    def update_offset(self,event=None):
        if self.isbinary:
            prev=self.contents.get("1.0",INSERT) # 获取从开头到光标处的文本
            try:
                data=to_bytes(prev)
            except SyntaxError:
                sep='\\'
                # self.update()
                prev=sep.join(prev.split(sep)[0:-1])
                try:data=to_bytes(prev)
                except SyntaxError:data=None
            if data is not None:
                self.status["text"]="偏移量: {} ({})"\
                                     .format(len(data),hex(len(data)))
        else:
            offset=self.contents.index(INSERT).split('.') # 不能用CURRENT
            self.status["text"]="Ln: {}  Col: {}".format(*offset)
    def _edit_decoded_event(self,event=None):
        self.after(20,self.edit_decoded) # 如果不使用after(),self.txt_decoded.get不会返回最新的值
    def edit_decoded(self):
        range_=self.contents.tag_ranges(SEL) # 获取选区
        if range_:
            start,end=range_[0].string,range_[1].string # 转换为字符串
        else:start=self.contents.index(INSERT);end=None
        try:
            coding=self.coding.get()
            if coding=="自动":
                msgbox.showinfo('','不支持自动编码, 请选择或输入其他编码',parent=self)
                return
            byte = self.txt_decoded.get('1.0',END)[:-1].encode(coding)
            esc_char = to_escape_str(byte,linesep=False)
            self.file_modified=True;self.change_title()
            if range_:
                self.contents.delete(start,end)
            self.contents.insert(start,esc_char)
            end = '%s+%dc'%(start, len(esc_char))
            self.contents.tag_add(SEL,start,end)
        except Exception as err:handle(err,parent=self)

    def new(self):
        try:self.saveconfig() # 保存配置，使新的窗口加载修改后的配置
        except OSError:pass
        window=Editor()
        window.focus_force()
        return window
    def new_binary(self):
        try:self.saveconfig()
        except OSError:pass
        window=Editor()
        window.isbinary=True
        window.create_binarytools()
        window.change_title()
        window.change_mode()
        window.contents.edit_reset()
        window.focus_force()
        return window
    def open(self):
        #打开一个文件
        #if self.ask_for_save(quit=False)==0:return
        filename=filediag.askopenfilename(master=self,title='打开',
                            initialdir=os.path.split(self.filename)[0],
                            filetypes=self.FILETYPES)
        if not filename:return
        if not self.filename and not self.file_modified: # 如果是刚新建的, 在当前窗口中打开
            self.load(filename)
        else:self.new().load(filename)
    def open_as_binary(self):
        #if self.ask_for_save(quit=False)==0:return
        filename=filediag.askopenfilename(master=self,title='打开二进制文件',
                            initialdir=os.path.split(self.filename)[0],
                            filetypes=self.FILETYPES)
        if not filename:return
        if not self.filename and not self.file_modified: # 如果是刚新建的
            self.load(filename,binary=True)
        else:self.new().load(filename,binary=True)
    def load(self,filename,binary=False):
        # 加载文件
        self.isbinary=binary
        try:
            data=self._load_data(filename)
            if data==0:return
            self.filename=filename
            self.contents.delete('1.0', END)
            if self.isbinary:
                self.contents.insert(INSERT,data)
            else:
                for char in data:
                    try:
                        self.contents.insert(INSERT,char)
                    except TclError:self.contents.insert(INSERT,' ')
            self.contents.mark_set(INSERT,"1.0")
            self.create_binarytools()
            self.file_modified=False
            self.change_title()
            self.change_mode()
            self.contents.edit_reset() # -*****- 1.2.5版: 重置文本框的撤销功能
            self.contents.focus_force()
        except Exception as err:handle(err,parent=self)
    def _load_data(self,filename):
        # 从文件加载数据
        f=open(filename,"rb")
        if self.isbinary:
            data=to_escape_str(f.read())
            return data
        else:
            try:
                #读取文件,并对文件内容进行编码
                raw=f.read()
                if self.coding.get()=="自动":
                    # 调用chardet库
                    encoding=chardet.detect(raw[:100000])['encoding']
                    if encoding is None:
                        encoding='utf-8'
                    self.coding.set(encoding)
                data=str(raw,encoding=self.coding.get())
            except UnicodeDecodeError:
                f.seek(0)
                result=msgbox.askyesnocancel("PyNotepad","""%s编码无法解码此文件,
是否使用二进制模式打开?"""%self.coding.get(),parent=self)
                if result:
                    self.isbinary=True
                    data=to_escape_str(f.read())
                elif result is not None:
                    self.isbinary=False
                    data=str(f.read(),encoding=self.coding.get(),errors="replace")
                else:
                    return 0 # 表示取消
            # return data.replace('\r','')
            return data
    def insert_hex(self):
        hex = simpledialog.askstring('',
                    "输入WinHex十六进制数据(如:00 1a 3d ff) :",parent=self)
        if hex is None:return
        try:
            data=bytes.fromhex(hex)
            self.contents.insert('insert',to_escape_str(data))
        except Exception as err:
            handle(err,parent=self)

    def change_title(self):
        file = os.path.split(self.filename)[1] or "未命名"
        newtitle="PyNotepad - "+ file +\
                  (" (二进制模式)" if self.isbinary else '') +\
                  (" (%s)" % self.filename if self.filename else '')
        if self.file_modified:
            newtitle="*%s*"%newtitle
        self.title(newtitle)
    def change_mode(self):
        if ColorDelegator:
            if self.filename.lower().endswith((".py",".pyw"))\
                   and (not self.isbinary):
                self._codefilter=ColorDelegator()
                if not self.colorobj:
                    self.colorobj=Percolator(self.contents)
                self.colorobj.insertfilter(self._codefilter)
                self.set_tag_bg()
            elif self.colorobj and self._codefilter.delegate:
                self.colorobj.removefilter(self._codefilter)
    def ask_for_save(self,quit=True):
        my_ret=None
        if self.file_modified: ## and self.filenamebox.get():
            retval=msgbox.askyesnocancel("文件尚未保存",
                              "是否保存{}的更改?".format(
                            os.path.split(self.filename)[1] or "当前文件"),
                                parent=self)
            if not retval is None:
                if retval==True:
                    # 是
                    ret=self.save()
                    # 在保存对话框中取消
                    if ret==0:
                        my_ret=0;quit=False
                # 否
            else:
                # 取消
                my_ret=0;quit=False  # 0表示cancel
        if quit:
            Editor.instances.remove(self)
            try:self.saveconfig()
            except OSError:pass
            self.destroy() # tkinter不会自动关闭窗口, 需调用函数手动关闭
        return my_ret
    def save(self):
        #保存文件
        if not self.filename:
            self.filename=filediag.asksaveasfilename(master=self,
                    initialdir=os.path.split(self.filename)[0],
                    filetypes=self.FILETYPES)
        filename=self.filename
        if filename.strip():
            try:
                text=self.contents.get('1.0', END)[:-1] # [:-1]: 去除末尾换行符
                if self.isbinary:
                    data=to_bytes(text)
                else:
                    data=bytes(text,encoding=self.coding.get(),errors='replace')
                    # Text文本框的bug:避免多余的\r换行符
                    # 如:输入文字foobar, data中变成\rfoobar
                    data=data.replace(b'\r',b'')
                with open(filename, 'wb') as f:
                    f.write(data)
                self.filename=filename
                self.file_modified=False
            except Exception as err:handle(err,parent=self)
            self.change_title()
            self.change_mode()
        else:
            return 0 # 0表示cancel
    def save_as(self):
        filename=filediag.asksaveasfilename(master=self,
                    initialdir=os.path.split(self.filename)[0],
                    filetypes=self.FILETYPES)
        if filename:
            self.filename=filename
            self.save()

    def about(self):
        msgbox.showinfo("关于",__doc__,parent=self)
    def feedback(self):
        msgbox.showinfo('PyNotepad',"""\
PyNotepad提供了多个反馈渠道。
若有反馈, 可以在 github.com/qfcy/Python 或 gitcode.net/qfcy_/Python 中创建issue。
或者在作者 blog.csdn.net/qfcy_ 的文章 "python tkinter.Text 高级用法 -- 设计功能齐全的文本编辑器" 中填写评论。
感谢您对PyNotepad项目的支持!""",parent=self)

    def loadconfig(self):
        try:
            with open(self.CONFIGFILE,'rb') as f:
                cfg=pickle.load(f)
                for key in cfg:
                    setattr(Editor,key,cfg[key])
        except OSError:
            pass
        # bug修复:未安装chardet时编码设为"自动"的情况
        if Editor.NORMAL_CODING=="自动" and not chardet:
            Editor.NORMAL_CODING="utf-8"
    def saveconfig(self):
        font=self.contents['font'].split(' ')
        cfg={'NORMAL_CODING':self.coding.get(),
             'NORMAL_FONT': self._get_fontname(),
             'NORMAL_FONTSIZE': int(font[-2]),
             'AUTOWRAP': self.contents['wrap'],
             'TEXT_BG':self.contents["bg"],
             'TEXT_FG':self.contents["fg"],
             "SHOW_STATUS":bool(self._show_status.get())}
        with open(self.CONFIGFILE,'wb') as f:
            pickle.dump(cfg,f)
    def onfiledrag(self,files):
        self.drag_files=files
        self.after(50,self.onfiledrag2)
    def onfiledrag2(self):
        self.saveconfig()
        if not self.filename and not self.file_modified: # 如果刚新建窗口
            self.load(self.drag_files[0].decode('ansi'))
            del self.drag_files[0]
        for item in self.drag_files:
            Editor(item.decode('ansi'))

def main():
    if sys.platform == 'win32': # Windows下的高DPI支持
        try:
            import ctypes
            PROCESS_SYSTEM_DPI_AWARE = 1
            ctypes.OleDLL('shcore').SetProcessDpiAwareness(PROCESS_SYSTEM_DPI_AWARE)
        except (ImportError, AttributeError, OSError):
            pass
    if len(sys.argv)>1:
        for arg in sys.argv[1:]:
            try:
                Editor(arg)
            except OSError:pass
    else: Editor()
    mainloop()

if __name__=="__main__":main()
