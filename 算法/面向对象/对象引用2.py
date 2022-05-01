import sys,gc,time

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
        #print("{} died".format(self))
        print('died')
        print('is_finalizing:',sys.is_finalizing())
        time.sleep(1)

def test():
    c=C()

if __name__=="__main__":
    c=C()
    print('Shutting down')
