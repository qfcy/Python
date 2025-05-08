import sys,gc,time,traceback

def debug(dict_):
    # 用来在交互式提示符中调试,参数dict_为命名空间
    while 1:
        s=input('>>> ').rstrip()
        if s:
            if s=='continue':break
            try:exec(compile(s,'<shell>','single'),dict_)
            except Exception:
                traceback.print_exc()
#lst=[]
class C:
    count=0
    def __init__(self):
        self.id=self.count
        C.count+=1
        print("{} was born".format(self))
    def __repr__(self):
        return object.__repr__(self)[:-1]+" id:%d>"%self.id
    def __del__(self):
        #lst.append(self)
        print("{} died".format(self),'is_finalizing',sys.is_finalizing())
        # 提示:解释器关闭过程中产生的所有异常都会被忽略，
        #      即显示Exception ignored in:...
        if sys.is_finalizing():
            debug(locals())

def test():
    while True:
        c=C()
        print()
        #time.sleep(0.1)

if __name__=="__main__":
    sys.c=C()
    test()
