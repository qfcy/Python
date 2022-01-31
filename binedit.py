"一款二进制文件编辑器,用于编辑二进制文件中的(可打印)字符串。"
import sys,os,re
import tkinter as tk
import tkinter.ttk as ttk

def extract_str(bytes,minlength=1,maxlength=1048576,encoding="utf-8",errors="replace"):
    "一个生成器,从二进制数据bytes中提取英文和中文字符串"
    string=str(bytes,encoding=encoding,errors=errors)
    patt=re.compile("([!-~]*|[㐀-龻]*)")
    for substr in re.findall(patt,string):
        if minlength<len(substr)<maxlength:yield substr

def is_chinese(string):
    """判断字符串中是否有中文(汉字)。
如果字符串中有中文,则返回True,否则返回False。"""
    for char in string:
        if 13312<ord(char)<40891:return True
    return False

class BinEditor:
    TITLE="二进制文件编辑器"
    def __init__(self,master,filename=None):
        self.master.title(self.TITLE)
        self.load_icon()
        self.create_widgets()

        self.filename=filename
        if filename:
            self.load(filename)
    def create_widgets(self):
        "创建控件"
        self.tvw=ScrolledTreeview(self.master,column='.')
        self.tvw.pack(expand=True,fill=tk.BOTH)
        self.tvw.heading("#0",text="属性")
        self.tvw.heading("#1",text="值")
        self.tvw.bind("<Double-Button-1>",self.on_doubleclick)
        self.tvw.tag_configure("error",foreground="red")  
