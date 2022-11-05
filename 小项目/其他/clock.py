"整点报时程序。"
import winsound,math,time

DELAY=0.2 #间隔时间(秒)
def bell(times):
    "调用winsound.Beep函数响铃(次数为times)。"
    for i in range(times):
        winsound.Beep(int(600*math.sin(i/6.28)+700),500)
        time.sleep(0.5)

def main():
    while True:
        t=time.localtime()
        hour,minute,second=str(t[3]).zfill(2),\
                            str(t[4]).zfill(2),\
                            str(t[5]).zfill(2)
        print("{}:{}:{}".format(hour,minute,second))
        #当前时间为整点时报时
        if second==0:
            bell(hour%12)
        time.sleep(DELAY)

if __name__=="__main__":main()
