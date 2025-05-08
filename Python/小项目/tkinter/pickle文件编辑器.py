import pickle,sys,os,re,pprint,subprocess
import pickletools
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as msgbox
import tkinter.filedialog as dialog
from tkinter.scrolledtext import ScrolledText
from io import StringIO

_TITLE="pickle数据文件编辑器"
_editors=[]
_pickle_file="*.pkl; *.pickle"
_FONT="宋体 12 normal"
_FILETYPE="pickle文件(%s)" % _pickle_file,_pickle_file
__version__='1.1.4'

class PklEditor:
    def __init__(self,master=None,filename=''):
        self.master=master or tk.Tk()
        self.master.title(_TITLE)
        self.master.protocol("WM_DELETE_WINDOW",self.ask_for_save)
        try:
            self.master.iconbitmap("pickle.ico")
        except:pass
        self.create_widgets(self.master)
        self.file_changed=False
        self.vars={}
        exec("from collections import *",self.vars)
        self.filename=''
        self.set_title()
        if filename:self.openfile(filename)
    def create_widgets(self,master):
        self.toolbar=tk.Frame(master)
        self.toolbar.pack(side=tk.BOTTOM)
        self.newbtn=ttk.Button(self.toolbar,text="新建",command=self.new)
        self.newbtn.pack(side=tk.LEFT)
        self.openbtn=ttk.Button(self.toolbar,text="打开",
                                command=self.ask_for_open)
        self.openbtn.pack(side=tk.LEFT)
        self.savebtn=ttk.Button(self.toolbar,text="保存",
                                command=self.save,state=tk.DISABLED)
        self.savebtn.pack(side=tk.LEFT)
        self.menubtn=ttk.Button(self.toolbar,text="菜单")
        self.menubtn.bind("<B1-ButtonRelease>",self.showmenu)
        self.menubtn.pack(side=tk.LEFT)
        menubtn=self.menubtn
        self.quitbtn=ttk.Button(self.toolbar,text="退出",
                                command=self.master.destroy)
        self.quitbtn.pack(side=tk.LEFT)

        self.text=ScrolledText(master,undo=True,font=_FONT,
                               width=70,height=22)
        self.text.pack(expand=True,fill=tk.BOTH)
        self.text.bind("<Key>",lambda event:self.master.after(80,self.text_change))
        self.text.focus_force()
        self.create_menu(self.text)
    def create_menu(self,master):
        self.menu=tk.Menu(master,tearoff=False)
        self.menu.add_command(label="剪切",
                         command=lambda:self.text_change() == master.event_generate("<<Cut>>"))
        self.menu.add_command(label="复制",
                         command=lambda:master.event_generate("<<Copy>>"))
        self.menu.add_command(label="粘贴",
                         command=lambda:self.text_change() == master.event_generate("<<Paste>>"))
        self.menu.add_separator()
        self.menu.add_command(label="代码检查",command=self.check_code,
                              state=tk.DISABLED)
        self.menu.add_command(label="用二进制模式打开",state=tk.DISABLED,
                              command=self.open_in_binarymode)
        self.menu.add_command(label="分析pickle文件内部结构",command=self.make_dis)
        self.use_optimization=tk.IntVar(self.master)
        self.use_optimization.set(1)
        self.menu.add_checkbutton(label="保存时自动优化文件",variable=self.use_optimization)
        master.bind("<Button-3>",self.showmenu)
    def showmenu(self,event):
        self.menu.post(event.x_root,event.y_root)
    @classmethod
    def new(cls):
        _editors.append(cls())
    def ask_for_open(self):
        filename=dialog.askopenfilename(
            master=self.master,
            filetypes=[_FILETYPE,("所有文件",'*')])
        if os.path.isfile(filename):
            if self.filename!=filename and self.text.get("1.0",tk.END)[:-1]:
                new=PklEditor()
                new.openfile(filename)
            else:self.openfile(filename)
    def openfile(self,filename):
        try:
            with open(filename,"rb") as f:
                #存在文件
                self.menu.entryconfig("用二进制模式打开",state=tk.NORMAL)
                self.filename=filename
                self.set_title()

                obj=pickle.load(f)
                self.text.delete("1.0",tk.END)
                contents=pprint.pformat(obj)
                self.text.insert(tk.INSERT,contents)
                self.import_modules(contents)
                self.file_changed=False
                self.menu.entryconfig("代码检查",state=tk.NORMAL)
                self.savebtn['state']=tk.NORMAL
        except Exception as err:
            msgbox.showinfo(type(err).__name__,
                            "无法打开文件: "+str(err))
        self.text.focus_force()

    def text_change(self,event=None):
        self.file_changed=True
        text=self.text.get("1.0",tk.END)[:-1]
        state = tk.NORMAL if text.strip() else tk.DISABLED
        self.menu.entryconfig("代码检查",state=state)
        self.savebtn['state']=state
        self.set_title()
    def import_modules(self,contents):
        # 自动检测输入内容中的xxx.xxx文字
        # 如: 这样用户可直接输入re.compile, 引用re模块的compile方法
        pat=re.compile("([A-Z]+|[a-z]+|[0-9]+)\\.([A-Z]+|[a-z]+|[0-9]+)")
        for modname,*_ in re.findall(pat,contents):
            try:
                exec("import %s"%modname,self.vars)
            except ImportError:
                msgbox.showinfo('',"无法导入模块: %s" % modname)
    def check_code(self):
        contents=self.text.get("1.0",tk.END)[:-1]
        self.import_modules(contents)
        try:
            eval(contents,self.vars)
        except Exception as err:
            msgbox.showinfo(type(err).__name__,
                            "您的代码有错误:\n"+str(err))
        else:
            msgbox.showinfo('代码检查',"您的代码没有错误。")
    def ask_for_save(self,quit=True):
        if self.file_changed:
            retval=msgbox.askyesnocancel("文件尚未保存",
                                         "是否保存{}的更改?".format(
                                             self.filename or "当前文件"))
            if retval is not None:
                if retval==True:self.save()
            else:return 0  #0:cancel
        if quit:self.master.destroy()
    def save(self):
        if not self.filename:
            self.filename=dialog.asksaveasfilename(
                master=self.master,
                defaultextension='.pkl',
                filetypes=[_FILETYPE, ("所有文件",'*')])
            if not self.filename:return -1 # -1 标识未保存
        res = self._save()
        if res!=-1:self.menu.entryconfig("用二进制模式打开",state=tk.NORMAL)
        return res
    def _save(self):
        text=self.text.get("1.0",tk.END)[:-1]
        if not text:return
        self.import_modules(text)
        try:
            obj=eval(text,self.vars)
            with open(self.filename,"wb") as f:
                if self.use_optimization.get():
                    optimized = pickletools.optimize(pickle.dumps(obj))
                    f.write(optimized)
                else:pickle.dump(obj,f)
            f.close()
            self.file_changed=False
        except Exception as err:
            msgbox.showinfo(type(err).__name__,
                            "无法保存文件{}: {}".format(
                            (", 您输入的数据格式有问题"
                            if type(err)==SyntaxError else ''),err))
            return -1
        else:self.set_title()
    def set_title(self):
        if self.file_changed:
            self.master.title("*%s - %s*" % (_TITLE,self.filename or 'Untitled'))
        else:
            self.master.title("%s - %s" % (_TITLE,self.filename or 'Untitled'))
    def open_in_binarymode(self):
        try:
            from pynotepad import Editor
            Editor(self.filename)
        except ImportError:
            if os.path.isfile("pynotepad.exe"):
                cmd = ("pynotepad.exe", self.filename)
            elif os.path.isfile("..\\pynotepad\\pynotepad.exe"):
                cmd = ("..\\pynotepad\\pynotepad.exe", self.filename)
            else:
                msgbox.showinfo('','缺少组件pynotepad.py或pynotepad.exe')
                return
            try:subprocess.Popen(cmd)
            except Exception as err:
                msgbox.showinfo(type(err).__name__,
                        "无法打开: "+str(err))
    def make_dis(self):
        if not self.file_changed or self.save() != -1:
            fout = StringIO()
            try:
                with open(self.filename,'rb') as f:
                    pickletools.dis(f,out = fout)
            except Exception as err:
                msgbox.showinfo(type(err).__name__,str(err))
                return
            fout.seek(0)
            result = fout.read()

            box = tk.Toplevel(self.master)
            text = ScrolledText(box)
            text.pack(expand=True,fill=tk.BOTH)
            text.insert('1.0',result)

def main():
    exe = os.path.split(sys.executable)
    if exe[1] not in ('python.exe','pythonw.exe'):# 程序已打包为exe
        try:os.chdir(exe[0])
        except OSError:pass
    if len(sys.argv)>1 and sys.argv[1]!='': # 修复用''空参数调用程序的bug
        for arg in sys.argv[1:]:
            if os.path.isfile(arg):
                root=tk.Tk()
                editor=PklEditor(root,filename=arg)
                _editors.append(editor)
    else:
        _editors.append(PklEditor())
    tk.mainloop()

if __name__ == "__main__":main()
