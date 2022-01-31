from io import BytesIO
from winsound import PlaySound,SND_MEMORY
import math,wave,struct
#import matplotlib.pyplot as plt

file = 'test.wav'
cache = {}

def generate(T,total,volume,sampwidth,sine=False):
    # T: 周期, total 总长度, 以帧为单位
    volume = min(volume * 2**(sampwidth*8),2**(sampwidth*8) - 1)
    if not sine:
        h = T / 2
        for i in range(total):
            if i % T >= h:
                yield volume
            else:
                yield 0
    else:
        w = 2 * math.pi  / T; r = volume / 2
        for i in range(total):
            # T = 2*pi / w
            yield int(math.sin(w * i) * r + r)

def Beep(frequency,duration,sine=False):
    global data
    if (frequency,duration) in cache:
        data=cache[(frequency,duration)]
    else:
        len_= duration / 1000 # 秒
        sampwidth = 2
        framerate = 22050
        volume = 1 # 音量, 0-1
        length = int(framerate * len_ * sampwidth)
        if sampwidth == 1: # 8位
            lst = list(generate(framerate / frequency, int(framerate*len_),
                            volume,sampwidth,sine))
            data = bytes(lst)
        elif sampwidth == 2:
            data = b'' # 16位
            lst = list(generate(framerate/frequency,
                                int(framerate*len_),
                                volume,sampwidth,sine))
            for digit in lst:
                data += struct.pack('<h',digit - 32768)

        f=BytesIO()
        fw = wave.open(f,'wb')
        fw.setnchannels(1)
        fw.setsampwidth(sampwidth)
        fw.setframerate(framerate)
        #fw.setnframes(length)
        fw.writeframes(data)

        f.seek(0);data=f.read()
        with open(file,'wb') as f:f.write(data)
        cache[(frequency,duration)]=data

    PlaySound(data,SND_MEMORY)

    #plt.plot(range(len(lst)),lst)
    #plt.show()

def test():
    Beep(220,1800,sine=True)

if __name__=='__main__':test()
