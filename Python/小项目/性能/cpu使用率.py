import time

USAGE=0.5
PERIOD=0.1 # 秒数

def do():pass

print("Cpu usage:%f%%"%(USAGE*100))
# 先重复调用do()函数, 然后根据预设的CPU使用率休眠一段时间
while True:
    time.sleep(PERIOD*(1-USAGE))
    s = time.perf_counter()
    while time.perf_counter()-s < PERIOD*USAGE:
        do()
