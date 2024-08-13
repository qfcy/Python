"A program that uses winsound module to play music."
import winsound,math,re,sys,time

music1="123 3 3 345 5 5  54321"
music2="53100 5310"
freqs=[None,264,297,330,352,396,440,495,528,556]

def music(notation,duration):
    patt=re.compile(r"([0-9](\-| ){0,8})")
    for pitch in re.findall(patt,notation):
        pitch=pitch[0]
        if pitch[0]=="0":time.sleep(duration/1000)
        else:
            yield freqs[int(pitch[0])],duration*len(pitch)

def sinewave(times,duration=100):
    pitch=None
    for i in range(times):
        pitch=int(math.sin(i/6.28)*600+700)
        yield pitch,duration

def __demo():
    for i in range(3):
        for freq,duration in music(music2,250):
            winsound.Beep(freq,duration)
        time.sleep(2.5)

def main():
    if len(sys.argv)>1:
        for arg in sys.argv[1:]:
            try:
                f=open(arg,"r",encoding="utf-8")
                for freq,duration in music(f.read(),250):
                    winsound.Beep(freq,duration)
                time.sleep(0.5)
            except OSError:pass
    else:__demo()

if __name__=="__main__":main()
