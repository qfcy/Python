import _thread,multiprocessing,time

##def loop():
##    i=0
##    while 1:
##        i+=1
##
##l=[]
##for i in range(3):
##    #_thread.start_new_thread(loop,())
##    p=multiprocessing.Process(target=loop)
##    p.start()
##    l.append(p)
##
##input()

USAGE=0.5
PERIOD=0.1 # seconds

def do():pass

print("Cpu usage:%f%%"%(USAGE*100))
while True:
    time.sleep(PERIOD*(1-USAGE))
    s = time.perf_counter()
    while time.perf_counter()-s < PERIOD*USAGE:
        do()
