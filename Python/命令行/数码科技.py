import sys,os,winsound,random,time
from winsound import PlaySound,SND_LOOP,SND_ASYNC

DELAY=0.08
def random_print(seq,num=40):
    chars=''
    for i in range(num):
        chars+=random.choice(seq)+'    '
    sys.stdout.write(chars)

def main():
    input("按Enter键开始 ...")
    
    filename="音乐.wav"
    if os.path.isfile(filename):
        PlaySound(filename,SND_LOOP+SND_ASYNC)
    try:
        import console_tool
        c=console_tool.Console()
        c.colorize(stdout="green")
    except ImportError:pass
    
    seq=open(os.__file__).readlines()
    try:
        while True:
            start=time.perf_counter()
            random_print(seq)
            cost=time.perf_counter()-start
            if cost<DELAY:time.sleep(DELAY-cost)
    except KeyboardInterrupt:pass

if __name__=="__main__":main()
