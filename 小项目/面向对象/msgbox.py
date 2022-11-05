"使用消息框代替sys.stdout等对象输出的程序"
import sys
from tkinter import Tk
from tkinter.messagebox import *

__ver__='1.1'
_root=None
_old_stdout=sys.stdout
_old_stderr=sys.stderr

class Stdout(object):
    def __init__(self,autoflush=False):
        self.autoflush=autoflush
        self.buffer=''
    def write(self,string):
        self.buffer+=string
        if self.autoflush:self.flush()
    def flush(self):
        if self.buffer and not self.buffer=='\n':
            showinfo("",self.buffer,master=_root)
        self.buffer=""

class Stderr(Stdout):
    def flush(self):
        if self.buffer and not self.buffer=='\n':
            showwarning("Error",self.buffer,master=_root)
        self.buffer=""

 # 初始化，使sys.stdout和sys.stderr对象输出到文本框
def init(stdout=True,stderr=True,autoflush=False,hide_root=True):
    global _root
    _root=Tk() # 使用root的目的是避免弹出消息框时多创建一个空白窗口
    if hide_root:
        _root.state('iconic')
        _root.withdraw()
    if stdout:sys.stdout=Stdout(autoflush)
    if stderr:sys.stderr=Stderr(autoflush)

def reset(): # 恢复原来的sys.stdout和sys.stderr对象
    sys.stdout=_old_stdout
    sys.stderr=_old_stderr

def main():
    init()
    print("Hello world!")
    raise

if __name__=="__main__":
    main()
    reset()
