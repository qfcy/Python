import sys,traceback
from tkinter import *
from tkinter.scrolledtext import ScrolledText

_old_stdout=sys.stdout
_old_stderr=sys.stderr
class Textbox(ScrolledText):
    def __init__(self):
        self.root=Tk()
        self.root.title(type(self).__name__)
        super().__init__(self.root)
        self.pack(fill=BOTH)
        self.tag_add("out",'0.0')
        self.tag_configure("out",foreground="blue")
        self.tag_add("err",'0.0')
        self.tag_config("err",foreground="red")

class Writer:
    def __init__(self,text,mode="out",autoflush=True):
        self.text=text
        self.mode=mode
        self.autoflush=autoflush
    def write(self,string):
        self.text.insert(END,string,self.mode)
        self.text.mark_set("insert",END)
        if self.autoflush:self.flush()
    def flush(self):
        self.text.root.update()
        self.text.yview('moveto',1)

def init(autoflush=True):
    text=Textbox()
    sys.stdout=Writer(text,'out',autoflush)
    sys.stderr=Writer(text,'err',autoflush)

def reset():
    sys.stdout=_old_stdout
    sys.stderr=_old_stderr

def test():
    import time

    init()
    for i in range(15):
        print("Hello world!")
        time.sleep(0.01)
    time.sleep(0.4)
    from random import randrange
    try:
        while True:
            str=""
            for n in range(50):
                #每次输出一行
                char=chr(randrange(0,55296))
                str+=char
            print(str,file=sys.stderr)
    except:
        traceback.print_exc() 
    sys.stderr.text.root.mainloop()

if __name__=="__main__":test()
