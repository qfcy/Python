"一个计时器模块,其中包含Timer类。"
import time

class Timer:
    def __init__(self):
        self.start()
    def start(self):
        "开始计时"
        self.time=time.time()
    def gettime(self):
        "获取从计时开始之后的时间"
        return time.time()-self.time
    def printtime(self):
        print("用时:",self.gettime(),"秒")

def test():
    print("------开始-----")
    print("每次执行循环1000000次,共20次:")
    t=Timer()
    total=Timer()
    for times in range(1,21):
        for n in range(1000000):pass
        print("第",times,"次用时:",t.gettime(),"秒")
        t.start()
    print("总用时:",total.gettime(),"秒",end="")

if __name__=="__main__":
    test()
    input()