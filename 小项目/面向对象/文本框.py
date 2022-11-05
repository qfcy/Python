"使用文本框代替sys.stdout等对象输出的程序"
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
        self.pack(expand=True,fill=BOTH)
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
        self.text.insert(END,string,self.mode) # 输出文字
        self.text.mark_set("insert",END) # 将光标移到文本末尾，以显示新输出的内容
        if self.autoflush:self.flush()
    def flush(self):
        self.text.root.update()
        self.text.yview('moveto',1)

def init(autoflush=True): # 初始化，使sys.stdout和sys.stderr对象输出到文本框
    text=Textbox()
    sys.stdout=Writer(text,'out',autoflush)
    sys.stderr=Writer(text,'err',autoflush)

def reset(): # 恢复原来的sys.stdout和sys.stderr对象
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
            for n in range(30):
                #每次输出一行
                char=chr(randrange(0,55296)) # 输出随机的字符
                str+=char
            print(str,file=sys.stderr)
    except:
        traceback.print_exc() 
    sys.stderr.text.root.mainloop()

if __name__=="__main__":test()
