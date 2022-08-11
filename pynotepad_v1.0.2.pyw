"""说明 Instructions:
A simple text editor written in Python.It supports editing text files,
binary files ,encodings and changing font size.
When you edit a binary file, the contents of the file are
displayed as escape sequences.
And code highlighting is supported when editing Python code files,like IDLE.

一款使用Python编写的文本编辑器, 支持编辑文本文件、二进制文件、改变字体大小。
支持ansi、gbk和utf-8编码。编辑二进制文件时, 文件内容以转义序列形式显示。
编辑python代码文件时, 也支持代码高亮显示, 类似IDLE。

作者:qfcy (七分诚意)
"""
import sys,os,time
from tkinter import *
from tkinter.scrolledtext import ScrolledText
import tkinter.ttk as ttk
import tkinter.messagebox as msgbox
import tkinter.filedialog as dialog

try:
    from idlelib.colorizer import ColorDelegator
    from idlelib.percolator import Percolator
except ImportError:
    ColorDelegator=Percolator=None


__all__=["directories","search"]
__email__="3076711200@qq.com"
__author__="七分诚意 qq:3076711200"
__version__="1.0.2"

#_REPLACE_CHARS=['\x00','\r']
def view_hex(bytes):
    result=''
    for char in bytes:
        result+= hex(char)[2:] + ' '
    return result
def _is_pythonfile(filename):
    python_ext=".py",".pyc",".pyw" #ext:文件扩展名
    for ext in python_ext:
        if filename.endswith(ext):return True
    return False

class SearchDialog(Toplevel):
    #查找对话框
    instances=[]
    def __init__(self,master):
        if not isinstance(master,Editor):
            raise TypeError("The master must be an Editor object, not %r."%(type(master).__name__))
        self.master=master
        self.coding=self.master.coding.get()
        cls=self.__class__
        cls.instances.append(self)
    def init_window(self,title="查找"):
        Toplevel.__init__(self,self.master)
        self.title(title)
        self.attributes("-toolwindow",True)
        self.attributes("-topmost",True)
        self.bind("<Destroy>",self.onquit)
    def show(self):
        self.init_window()
        frame=Frame(self)
        ttk.Button(frame,text="查找下一个",command=self.search).pack()
        ttk.Button(frame,text="退出",command=self.destroy).pack()
        frame.pack(side=RIGHT,fill=Y)
        inputbox=Frame(self)
        Label(inputbox,text="查找内容:").pack(side=LEFT)
        self.keyword=StringVar()
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
        self.use_regexpr=IntVar()
        ttk.Checkbutton(master,text="使用正则表达式",variable=self.use_regexpr)\
        .pack(side=LEFT)
        self.match_case=IntVar()
        ttk.Checkbutton(master,text="区分大小写",variable=self.match_case)\
        .pack(side=LEFT)
        self.use_escape_char=IntVar()
        self.use_escape_char.set(self.master.isbinary)
        ttk.Checkbutton(master,text="转义字符",variable=self.use_escape_char)\
        .pack(side=LEFT)
    
    def search(self,event=None,mark=True,bell=True):
        text=self.master.contents
        key=self.keyword.get()
        if not key:return
        if self.use_escape_char.get():
            key=repr(bytes(eval("'%s'"%key),encoding=self.coding))[2:-1]
        text.tag_remove("sel","1.0",END)
        pos=text.search(key,INSERT,END,
                        regexp=self.use_regexpr.get(),
                        nocase=not self.match_case.get())
        if pos:
            newpos="%s+%dc"%(pos,len(key))
            text.mark_set(INSERT,newpos)
            if mark:self.mark_text(pos,newpos)
            return pos,newpos
        elif bell:self.bell()
    def mark_text(self,start_pos,end_pos):
        text=self.master.contents
        text.tag_add("sel",start_pos,end_pos)
        text.focus_force()
        self.master.update_status()
    def onquit(self,event):
        cls=self.__class__
        if self in cls.instances:
            cls.instances.remove(self)

class ReplaceDialog(SearchDialog):
    #替换对话框
    instances=[]
    def show(self):
        self.init_window(title="替换")
        frame=Frame(self)
        ttk.Button(frame,text="替换",command=self.replace).pack()
        ttk.Button(frame,text="全部替换",command=self.replace_all).pack()
        ttk.Button(frame,text="退出",command=self.destroy).pack()
        frame.pack(side=RIGHT,fill=Y)
        
        inputbox=Frame(self)
        Label(inputbox,text="查找内容:").pack(side=LEFT)
        self.keyword=StringVar()
        keyword=ttk.Entry(inputbox,textvariable=self.keyword)
        keyword.pack(side=LEFT,expand=True,fill=X)
        keyword.focus_force()
        inputbox.pack(fill=X)
        
        replace=Frame(self)
        Label(replace,text="替换为:  ").pack(side=LEFT)
        self.text_to_replace=StringVar()
        replace_text=ttk.Entry(replace,textvariable=self.text_to_replace)
        replace_text.pack(side=LEFT,expand=True,fill=X)
        replace_text.bind("<Key-Return>",self.replace)
        replace.pack(fill=X)
        
        options=Frame(self)
        self.create_options(options)
        options.pack(fill=X)
    def replace(self,bell=True):
        text=self.master.contents
        result=self.search(mark=False,bell=bell)
        if not result:return -1 #-1标志已无文本可替换
        pos,newpos=result
        newtext=self.text_to_replace.get()
        if self.use_escape_char.get():
            newtext=repr(bytes(eval("'%s'"%newtext),encoding=self.coding))[2:-1]
        text.delete(pos,newpos)
        text.insert(pos,newtext)
        end_pos="%s+%dc"%(pos,len(newtext))
        self.mark_text(pos,end_pos)
        
    def replace_all(self):
        while self.replace(bell=False)!=-1:pass
     
class Editor(Tk):
    TITLE="PyNotepad"
    encodings="ansi","utf-8","utf-16","utf-32","gbk","big5"
    ICON="notepad.ico"
    NORMAL_CODING="utf-8"
    FONTSIZES=8, 9, 10, 11, 12, 14, 18, 20, 22, 24, 30
    NORMAL_FONT='宋体'
    NORMAL_FONTSIZE=11
    windows=[]
    def __init__(self,filename=""):
        super().__init__()
        self.title(self.TITLE)
        self.bind("<Key>",self.window_onkey)
        self.bind("<FocusIn>",self.focus)
        self.bind("<FocusOut>",self.focus)
        self.protocol("WM_DELETE_WINDOW",self.ask_for_save)
        self.isbinary=self.file_changed=False
        self.bin_data=self.charmap=None
        self.colorobj=None
        
        self.load_icon()
        self.create_widgets()
        self.update()
        self.filename=''
        Editor.windows.append(self)
        if filename:
            self.filenamebox.insert(END,filename)
            self.load()
    def load_icon(self):
        for path in sys.path:
            try:
                self.iconbitmap("{}\{}".format(path,self.ICON))
            except TclError:pass
            else:break
    def create_widgets(self):
        # 创建控件
        self.statusbar=Frame(self)
        self.statusbar.pack(side=BOTTOM,fill=X)
        self.status=Label(self.statusbar,justify=RIGHT)
        self.status.pack(side=RIGHT)
        
        frame=Frame(self)
        frame.pack(side=TOP,fill=X)
        self.filenames=[]
        self.filenamebox = ttk.Combobox(frame)
        self.filenamebox["value"]=list(reversed(self.filenames))
        self.filenamebox.pack(side=LEFT, expand=True, fill=X)
        self.filenamebox.bind("<Key>",self.filenamebox_onkey)
        self.filenamebox.focus_force()
        
        ttk.Button(frame,text='新建', command=self.new,width=7).pack(side=LEFT)
        ttk.Button(frame,text='打开', command=self.load,width=7).pack(side=LEFT)
        ttk.Button(frame,text='保存', command=self.save,width=7).pack(side=LEFT)
        self.run_btn=ttk.Button(frame,width=0,state=DISABLED,command=self.run)
        self.run_btn.pack(side=LEFT)
        
        self.options=Frame(self)
        self.options.pack(side=TOP,fill=X)
        self.create_options(self.options)
        
        self.contents=ScrolledText(self,undo=True,width=75,height=24,
                                   font=(self.NORMAL_FONT,self.NORMAL_FONTSIZE,"normal"))
        self.contents.pack(expand=True,fill=BOTH)
        self.contents.bind("<Key>",self.text_change)
        self.contents.bind("<B1-ButtonRelease>",self.update_status)
        self.update_offset()
        
        self.create_menu()
    def create_options(self,master):
        self.is_binmode=IntVar()
        ttk.Radiobutton(master,text="文本模式",
                    variable=self.is_binmode,value=0).pack(side=LEFT)
        ttk.Radiobutton(master,text="二进制模式",
                    variable=self.is_binmode,value=1).pack(side=LEFT)
        
        Label(master,text="编码:").pack(side=LEFT)
        self.coding=StringVar()
        self.coding.set(self.NORMAL_CODING)
        coding=ttk.Combobox(master,textvariable=self.coding)
        coding["value"]=self.encodings
        coding.pack(side=LEFT)
    def create_binarytools(self):
        if self.isbinary:
            if not self.bin_data:
                self.bin_data=ScrolledText(self.statusbar,width=8,height=6)
            if not self.charmap:
                self.charmap=ScrolledText(self.statusbar,width=20,height=5)
            self.bin_data.pack(side=LEFT,expand=True,fill=BOTH)
            self.charmap.pack(fill=Y)
            self.status.pack_forget()
            self.status.pack(fill=X)
        else:
            if self.bin_data:
                self.bin_data.pack_forget()
            if self.charmap:
                self.charmap.pack_forget()
            self.status.pack(side=RIGHT)
    def create_menu(self):
        self.basemenu=self._new_menu(self.filenamebox)
        self.basemenu.add_separator()
        self.basemenu.add_command(label="浏览 ...",command=self.browse_file)
        
        self.editmenu=self._new_menu(self.contents)
        self.editmenu.add_separator()
        self.editmenu.add_command(label="查找",accelerator="Ctrl+F",
                                  command=lambda:self.show_dialog(SearchDialog))
        self.editmenu.add_command(label="替换",
                                  command=lambda:self.show_dialog(ReplaceDialog))
        self.editmenu.add_separator()
        
        fontsize=Menu(self.contents,tearoff=False)
        fontsize.add_command(label="增大字体   ",accelerator='Ctrl+ "+"',
                             command=self.increase_font)
        fontsize.add_command(label="减小字体   ",accelerator='Ctrl+ "-"',
                             command=self.decrease_font)
        fontsize.add_separator()
        
        for i in range(len(self.FONTSIZES)):
            def resize(index=i):
                self.set_fontsize(index)
            fontsize.add_command(label=self.FONTSIZES[i],command=resize)
        
        self.editmenu.add_cascade(label="字体",menu=fontsize)
        
    def _new_menu(self,master,tearoff=False,**options):
        menu=Menu(master,tearoff=tearoff,**options)
        menu.add_command(label="剪切  ",accelerator="Ctrl+X",
                         command=lambda:self.text_change()==master.event_generate("<<Cut>>"))
        menu.add_command(label="复制  ",accelerator="Ctrl+C",
                         command=lambda:master.event_generate("<<Copy>>"))
        menu.add_command(label="粘贴  ",accelerator="Ctrl+V",
                         command=lambda:self.text_change()==master.event_generate("<<Paste>>"))
        master.bind("<Button-3>",
                    lambda event:menu.post(event.x_root,event.y_root))
        return menu
    def browse_file(self):
        filename=dialog.askopenfilename(master=self)
        self.filenamebox.delete(0,END)
        self.filenamebox.insert(0,filename)
    def show_dialog(self,dialog_type):
        # dialog_type is the class of the dialog
        for window in dialog_type.instances:
            if window.master is self:
                window.focus_force()
                return
        dialog_type(self).show()
    
    def set_fontsize(self,index):
        newsize=self.FONTSIZES[index]
        self.contents["font"]=(self.NORMAL_FONT,newsize,"normal")
    def increase_font(self):
        "增大字体"
        fontsize=int(self.contents["font"].split()[1])
        index=self.FONTSIZES.index(fontsize)+1
        if 0<=index<len(self.FONTSIZES): self.set_fontsize(index)
    def decrease_font(self):
        "减小字体"
        fontsize=int(self.contents["font"].split()[1])
        index=self.FONTSIZES.index(fontsize)-1
        if 0<=index<len(self.FONTSIZES): self.set_fontsize(index)

    
    def filenamebox_onkey(self,event):
        if event.char=='\r':self.load()
    def window_onkey(self,event):
        if event.state==4:#如果按下Ctrl键
            if event.keysym=='o':#按下Ctrl+O键
                self.load()
            elif event.keysym=='s':#Ctrl+S键
                self.save()
            elif event.keysym=='z':#Ctrl+Z
                try:self.contents.edit_undo()
                except TclError:self.bell()
                self.text_change()
            elif event.keysym=='y':#Ctrl+Y
                try:self.contents.edit_redo()
                except TclError:self.bell()
                self.text_change()
            elif event.keysym=='f':#Ctrl+F
                self.show_dialog(SearchDialog)
            elif event.keysym=='equal':#Ctrl+ "+"
                self.increase_font()
            elif event.keysym=='minus':#Ctrl+ "-"
                self.decrease_font()
    def focus(self,event):
        #当窗口获得或失去焦点时,调用此函数
        for window in SearchDialog.instances + ReplaceDialog.instances:
            if window.master is self:
                if event.type==EventType.FocusIn:
                    if window.wm_state()=="iconic":
                        window.attributes("-toolwindow",True)
                    window.attributes("-topmost",True)
                    window.deiconify()
                else:
                    window.attributes("-topmost",False)
                    if self.wm_state()=="iconic":
                        window.withdraw()
                        #window.iconify()
                break

    def text_change(self,event=None):
        self.file_changed=True
        self.update_offset()
    def update_status(self,event=None):
        if self.isbinary:
            try:
                selected=self.contents.get(SEL_FIRST,SEL_LAST)
                data=eval("b'''"+selected+"'''")
                try:
                    text=str(data,encoding=self.coding.get(),
                             errors="backslashreplace")
                except TypeError:
                    text=''
                self.bin_data.delete("1.0",END)
                self.bin_data.insert(INSERT,text)
                self.charmap.delete("1.0",END)
                self.charmap.insert(INSERT,view_hex(data))
                self.status["text"]="选区长度: %d (Bytes)"%len(data)
            except (TclError,SyntaxError): #未选取内容
                self.update_offset()
        else:self.update_offset()
    def update_offset(self,event=None):
        if self.isbinary:
            selected=self.contents.get("1.0",INSERT)
            try:
                data=eval("b'''"+selected+"'''")
            except SyntaxError:
                sep='\\'
                selected=sep.join(selected.split(sep)[0:-1])
                data=eval("b'''"+selected+"'''")
            self.status["text"]="偏移量: {} ({})".format(len(data),hex(len(data)))
        else:
            offset=self.contents.index(CURRENT).split('.')
            self.status["text"]="Ln: {}  Col: {}".format(*offset)

    @classmethod
    def new(cls):
        window=cls()
        window.focus_force()
    def load(self):
        #加载一个文件
        filename=self.filenamebox.get()
        if not filename.strip():
            msgbox.showinfo("","必须输入文件名!")
            return
        if os.path.isfile(filename):
            self.filename=filename
            data=self._load_data(filename)
            if len(data)>100000:self.title(
                "%s - 加载中,请耐心等待..." % self.TITLE)
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
            self.change_title()
            self.change_mode()
            self.filenames.append(filename)
            self.filenamebox["value"]=list(reversed(self.filenames))
            self.contents.focus_force()
        else:msgbox.showinfo("Error","文件未找到:"+repr(filename))
    def _load_data(self,filename):
        f=open(filename,"rb")#打开文件
        if self.is_binmode.get():
            self.isbinary=True
            return repr(f.read())[2:-1]
        try:
            #读取文件,并对文件内容进行编码
            data=str(f.read(),encoding=self.coding.get())
            self.isbinary=False
        except UnicodeDecodeError:
            f.seek(0)
            result=msgbox.askyesno("","""%s编码无法解码此文件,
是否使用二进制模式打开?"""%self.coding.get())
            if result:
                self.isbinary=True
                data=repr(f.read())[2:-1]
                
                #data=str(f.read(),encoding=self.coding.get(),
                #         errors="backslashreplace")
                #for char in _REPLACE_CHARS:
                #    print(repr(char)[1:-1])
                #    data.replace(char,repr(char)[1:-1])
            else:
                self.isbinary=False
                data=str(f.read(),encoding=self.coding.get(),errors="replace")
        return data
    def change_title(self,running=False):
        newtitle="PyNotepad - "+os.path.split(self.filename)[1]+\
                  (" (二进制模式)" if self.isbinary else '')+\
                  (" (运行)" if running else '')
        self.title(newtitle)
    def change_mode(self):
        if  _is_pythonfile(self.filename):
            self.run_btn["state"]=NORMAL
            self.run_btn["text"]='运行程序' 
        else:
            self.contents.tag_delete("all")
            self.run_btn["state"]=DISABLED
            self.run_btn["text"]=''
        if ColorDelegator:
            if ( self.filename.endswith(".py") or self.filename.endswith(".pyw"))\
               and (not self.isbinary):
                self._codefilter=ColorDelegator()
                if not self.colorobj:
                    self.colorobj=Percolator(self.contents)
                self.colorobj.insertfilter(self._codefilter)
            elif self.colorobj and self._codefilter:
                self.colorobj.removefilter(self._codefilter)
    def ask_for_save(self,quit=True):
        if self.file_changed and self.filenamebox.get():
            retval=msgbox.askyesnocancel("文件尚未保存",
                              "是否保存{}的更改?".format(
                                  os.path.split(self.filename)[1] or "当前文件"))
            if not retval is None:
                if retval==True:self.save()
            else:return 0  #0:cancel
        if quit:
            Editor.windows.remove(self)
            self.destroy()
    def save(self):
        #保存文件
        filename=self.filenamebox.get()
        if filename.strip():
            text=self.contents.get('1.0', END)[:-1]
            if self.isbinary:
                data=eval('b"""'+text+'"""')
            else:data=bytes(text,encoding=self.coding.get())
            file=open(filename, 'wb')
            file.write(data)
            file.close()
            self.filename=filename
            self.file_changed=False
            self.change_title()
            self.change_mode()
            if filename not in self.filenames:
                self.filenames.append(filename)
                self.filenamebox["value"]=list(reversed(self.filenames))
    def run(self):
        import _thread
        try:
            import console
            c=console.Console()
            c.colorize()
        except:pass
        def _run():
            self.change_title(running=True)
            start=time.perf_counter()
            try:
                if os.path.isfile(os.getenv("systemroot")+"\py.exe"):
                    returnval=os.system("py %s" % self.filename)
                else:returnval=os.system("python %s" % self.filename)

                print("END with return value {}(用时:{:.6f}秒)".format(
                    returnval,time.perf_counter()-start),file=sys.stderr)
            except KeyboardInterrupt:print("STOPPED!",file=sys.stderr)
            self.change_title(running=False)
        filename=getattr(self,"filename",'')
        if filename:
            print("START:"+filename)
            _thread.start_new_thread(_run,())

def main():
    def _mainloop():
        try:mainloop()
        except KeyboardInterrupt:_mainloop()
    if len(sys.argv)>1:
        for arg in sys.argv[1:]:
            try:
                Editor(arg)
            except OSError:pass
    else: Editor()
    _mainloop()

if __name__=="__main__":main()
