import sys,traceback
from tkinter import *
from tkinter.scrolledtext import ScrolledText

_old_stdout=sys.stdout
_old_stderr=sys.stderr
class Textbox(ScrolledText):
    def __init__(self,mode="out",autoflush=True):
        self.root=Tk()
        self.root.title("%s  (mode=%s)" %(type(self).__name__,mode))
        super().__init__(self.root)
        self.pack(fill=BOTH)
        self.tag_add("out",'0.0')
        self.tag_configure("out",foreground="blue")
        self.tag_add("err",'0.0')
        self.tag_config("err",foreground="red")
        self.text=""
        self.mode=mode
        self.autoflush=autoflush
    def write(self,string):
        self.insert(END,string,self.mode)
        self.mark_set("insert",END)
        if self.autoflush:self.flush()
    def flush(self):
        self.root.update()
    def read(self):
        return self.get("1.0",END)[0:-1]

def init(autoflush=True):
    sys.stdout=Textbox("out",autoflush)
    sys.stderr=Textbox("err",autoflush)

def reset():
    sys.stdout=_old_stdout
    sys.stderr=_old_stderr

def test():
    import time
    try:import 算法.无限输出 as 无限输出
    except:无限输出=None

    init()
    for i in range(15):
        print("Hello world!")
        time.sleep(0.01)
    time.sleep(0.4)
    if 无限输出:
        try:
            while True:
                无限输出.print()
                print()
        except:
            traceback.print_exc() 
    sys.stderr.root.mainloop()

if __name__=="__main__":test()
