"使用消息框输出的工具"
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

def init(stdout=True,stderr=True,autoflush=False,hide_root=True):
    global _root
    _root=Tk()
    if hide_root:
        _root.state('iconic')
        _root.withdraw()
    if stdout:sys.stdout=Stdout(autoflush)
    if stderr:sys.stderr=Stderr(autoflush)

def reset():
    sys.stdout=_old_stdout
    sys.stderr=_old_stderr

def main():
    init()
    print("Hello world!")
    raise

if __name__=="__main__":
    main()
    reset()
