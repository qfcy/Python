import sys,gc,time

def debug(dict_):
    while 1:
        s=input('>>> ').rstrip()
        if s:
            if s=='continue':break
            try:exec(compile(s,'<shell>','single'),dict_)
            except Exception as err:
                print(type(err).__name__+':'+str(err))
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
