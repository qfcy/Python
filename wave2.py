import wave
from io import BytesIO
from winsound import PlaySound,SND_MEMORY

file = 'test.wav'
cache = {}
def Beep(frequency,duration):
    if (frequency,duration) in cache:
        data=cache[(frequency,duration)]
    else:
        len_= duration / 1000 # 秒
        sampwidth = 1
        framerate = 22050
        length = int(framerate * len_ * sampwidth)
        para = [0b00000000]*(framerate//frequency//2*sampwidth)\
               +[0b11111111]*(framerate//frequency//2*sampwidth)
        data=bytes(para)

        f=BytesIO()
        fw = wave.open(f,'wb')
        fw.setnchannels(1)
        fw.setsampwidth(sampwidth)
        fw.setframerate(framerate)
        #fw.setnframes(length)
        fw.writeframes(data * (length // len(data)))

        f.seek(0);data=f.read()
        with open(file,'wb') as f:f.write(data)
        cache[(frequency,duration)]=data

    PlaySound(data,SND_MEMORY)

def test():
    Beep(100,1700)

if __name__=='__main__':test()
