from io import BytesIO
from winsound import PlaySound,SND_MEMORY
import math,wave,struct
from random import random

__all__=["generate_sine","generate_triangular","generate_square",
         "generate_white_noise","mixer","wave_mixer","Beep",
         "to_raw_data","to_wav_data","view_wave"]

SINE_WAVE=0
TRIANGULAR_WAVE=1
SQUARE_WAVE=2

# 程序中，生成器生成的值为整数，8位时范围为0~255,16位时为0~65535

# 生成正弦波
def generate_sine(freq,seconds,volume,samprate,sampwidth,phase=0):
    # phase:声波相位，即波形左移多少，范围为0~2π
    # 8位时，生成值的范围是0~255，16位时则为0~65535
    sin = math.sin; mid = 1<<(sampwidth*8-1) # mid为128或32768
    A = min((1<<(sampwidth*8-1)) * volume, (1<<(sampwidth*8-1)) - 1) # 振幅,min的作用为防止溢出
    count = int(samprate * seconds)
    T = samprate / freq; w = 2 * math.pi / T
    for i in range(count):
        yield int(A * sin(w * i + phase) + mid)

# 生成三角波
def generate_triangular(freq,seconds,volume,samprate,sampwidth):
    T = samprate / freq; half = T / 2 # T: 周期
    count = int(samprate * seconds) # count: 总长度, 以帧为单位
    A = min((1<<(sampwidth*8-1)) * volume, (1<<(sampwidth*8-1)) - 1)
    for i in range(count):
        yield int((half - abs(i % T - half)) * 2 * A / half)
# 生成方波
def generate_square(freq,seconds,volume,samprate,sampwidth):
    mid = 1<<(sampwidth*8-1) # mid为128或32768
    T = samprate / freq; half = T / 2 # T: 周期
    count = int(samprate * seconds)
    A = min((1<<(sampwidth*8-1)) * volume, (1<<(sampwidth*8-1)) - 1)
    high = mid + A; low = mid - A
    for i in range(count):
        if i % T >= half:
            yield high
        else:
            yield low

_generator_types={SINE_WAVE:generate_sine,
                  TRIANGULAR_WAVE:generate_triangular,
                  SQUARE_WAVE:generate_square}

# 生成白噪声
def generate_white_noise(volume,seconds,samprate,sampwidth):
    count = int(samprate * seconds)
    mid = 1<<(sampwidth*8-1)
    A = min((1<<(sampwidth*8-1)) * volume, (1<<(sampwidth*8-1)) - 1)
    for _ in range(count):
        yield int(random() * 2 * A + (mid - A))

# 对上一层的声音进行积分
def integral(generator,volume,sampwidth):
    maxval = (1<<(sampwidth*8)) - 1; minval=0 # 最大和最小范围
    mid = 1<<(sampwidth*8-1) # 中间值
    A = min((1<<(sampwidth*8-1)) * volume, (1<<(sampwidth*8-1)) - 1)
    rate = A / (maxval - minval)
    value=mid # 初始值
    for dt in generator: # 上一层级的生成器
        dt=(dt-mid)*rate
        if minval<=value+dt<=maxval:
            value+=dt
        elif minval<=value-dt<=maxval:
            value-=dt
        yield int(value)

def get_wav_info(filename):
    # 获取wav文件的信息
    with wave.open(filename,'rb') as f:
        sampwidth = f.getsampwidth()
        samprate=f.getframerate()
        seconds=f.getnframes()/samprate
    return samprate,sampwidth,seconds

def read_wav(filename):
    # 读取音频(目前仅支持单声道)
    with wave.open(filename,'rb') as f:
        sampwidth = f.getsampwidth()
        nframes=f.getnframes()
        from_bytes=int.from_bytes
        signed=True if sampwidth==2 else False
        offset=32768 if sampwidth==2 else 0
        for i in range(nframes):
            data=f.readframes(1)
            value=from_bytes(data,"little",signed=signed) + offset
            yield value

def convert(generator,from_samprate,from_sampwidth,to_samprate,to_sampwidth):
    # 转换一段波形的采样率和量化位数
    factor=2**((to_sampwidth-from_sampwidth)*8)
    step=from_samprate/to_samprate
    pre=-1;cur=0 # 哨兵
    pre_value=-1;value=next(generator)
    while True:
        if int(cur)>int(pre):
            # 取生成器后面的值
            try:
                for i in range(int(cur)-int(pre)):
                    pre_value=value
                    value=next(generator)
            except StopIteration:
                if i==int(cur)-int(pre)-1 and (cur % 1) / step < 1e-5: # 判断是否需返回最后一项，同时避免浮点误差
                    yield value # 返回最后一项
                break
        weight = cur % 1
        output = int((pre_value * (1-weight) + value * weight) * factor)
        yield output
        pre=cur
        cur+=step

def adjust_volume(generator,sampwidth,volume): # 调整音频的音量 (振幅)
    mid = 1<<(sampwidth*8-1) # 中间值
    for value in generator:
        yield int((value - mid) * volume + mid)

def concat(*generators): # 按顺序拼接多段声音，采样频率和位数需要相同
    for gen in generators:
        for value in gen:
            yield value

def reverse(generator): # 反转一段声音
    lst=list(generator)
    return reversed(lst)

def mixer(generators):
    # 混音器，混合多个音频生成器的输出
    # generators为一个列表，每一项是一个元组，包含一个迭代器和一个0~1的振幅
    while True:
        i=0;value=0
        while i<len(generators):
            try:
                val=next(generators[i][0])
                value+=val*generators[i][1]
                i+=1
            except StopIteration:
                del generators[i] # 此时i不加1
        if not generators:return
        yield int(value)

def wave_mixer(sounds,seconds,volume,samprate,sampwidth):
    # 波形混合器。sounds为一个列表，
    # 每一项是元组，元组的项分别是声波类型、频率、声音响度(分贝)
    generators=[]
    for type,freq,db in sounds:
        vol = 1 * 10**(db/20)
        generators.append((_generator_types[type](
            freq,seconds,1,samprate,sampwidth),vol*volume))
    return mixer(generators)

def fourier_transform(generator,freq,samprate,sampwidth): # 傅里叶变换
    mid = 1<<(sampwidth*8-1) # 中间值
    rate = 1<<(sampwidth*8)
    total=0; t=0; pi=math.pi; e=math.e
    for value in generator:
        value = (value - mid) / rate
        total += value * e ** (-2j * pi * t * freq) # 积分
        t += 1/samprate
    magnitude = math.hypot(total.real, total.imag)/samprate
    phase = math.atan2(total.imag, total.real)
    return magnitude, phase


def to_raw_data(generator,sampwidth,size):
    # 根据量化位宽，将生成器的输出转换为原始音频数据
    if sampwidth==1:
        return bytes(generator) # 8位时，wav音频帧的范围为0~255
    else:
        arr=bytearray(size);offset=0 # 使用bytearray提升性能
        pack_into=struct.pack_into
        for value in generator:
            pack_into('<h',arr,offset,value-32768) # 16位时，音频帧范围为-32768~32767
            offset += sampwidth
        return bytes(arr)

def to_wav_data(raw_data,samprate,sampwidth,channels=1):
    # 根据原始数据，构造wav文件的数据，包括wav的文件头
    f=BytesIO() # 创建文件对象
    fw = wave.open(f,'wb')
    fw.setnchannels(channels)
    fw.setframerate(samprate)
    fw.setsampwidth(sampwidth)
    #fw.setnframes(samprate * seconds * sampwidth)
    fw.writeframes(raw_data)
    f.seek(0);return f.read() # 读取写入的数据

def view_wave(generator,seconds): # 显示波形
    try:
        import numpy as np # 由于导入matplotlib等库耗时较长，就在函数内导入，而不是开头
        import matplotlib.pyplot as plt
    except ImportError:
        raise NotImplementedError("Missing optional libraries: numpy and matplotlib")
    plt.rcParams['font.sans-serif'] = ['SimHei'] # 用于正常显示中文
    plt.rcParams["axes.unicode_minus"]=False

    data=list(generator)
    lsp=np.linspace(0,seconds,len(data),endpoint=False)
    fig=plt.figure()
    plt.plot(lsp,data)
    plt.title("生成的声波")
    plt.xlabel("时间(s)")
    plt.ylabel("振幅")
    fig.canvas.set_window_title("生成的声波")
    plt.show()

def view_freq_spectrum(generator,samprate,sampwidth,min=10,max=10000,count=100): # 显示频谱
    try:
        import numpy as np
        import matplotlib.pyplot as plt
    except ImportError:
        raise NotImplementedError("Missing optional libraries: numpy and matplotlib")
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams["axes.unicode_minus"]=False

    lsp=np.linspace(math.log10(min), math.log10(max), count)
    lsp=10 ** lsp
    data=list(generator)
    transformed=[]
    for freq in lsp:
        transformed.append(fourier_transform(data,freq,samprate,sampwidth))
    mag_db=[math.log10(x[0])*20 for x in transformed]
    phase=[x[1] for x in transformed]
    fig, ax1 = plt.subplots()

    ax1.plot(lsp,mag_db,label="幅度(dB)",color="blue")
    ax1.set_xscale('log')
    ax1.set_xlabel("频率(Hz)")
    ax1.set_ylabel("幅度(dB)")

    ax2=ax1.twinx()
    ax2.plot(lsp,phase,label="相位(弧度)",color="orange")
    ax2.set_ylabel("相位(弧度)")
    ax2.set_ylim(-math.pi,math.pi*16)

    plt.title("生成声波的傅里叶变换") # 也可用fig.suptitle
    fig.canvas.set_window_title("生成声波的傅里叶变换")
    fig.legend()
    plt.show()

_beep_cache={}
def Beep(frequency,duration,type=SINE_WAVE,use_cache=True):
    # 发出一段声音，替代winsound.Beep函数，其中duration为毫秒数
    if use_cache and (frequency,duration,type) in _beep_cache:
        wav_data = _beep_cache[(frequency,duration,type)]
    else:
        seconds = duration / 1000 # 音频长度(秒)
        sampwidth = 2 # 量化位宽(字节)，现仅支持1或2
        samprate = 22050 # 采样频率
        # 音量的分贝数(dB)，取值为负数或0，0为最大音量。
        volume_db = 0 # 分贝数每降低20，声音振幅减小10倍
        volume = 1 * 10**(volume_db/20) # 声音的振幅, 取值范围为0 ~ 1，1为最大
        size = int(samprate * seconds * sampwidth) # 音频总大小(字节)
        # 构造声波生成器
        if type==SINE_WAVE:
            gen = generate_sine(frequency,seconds,volume,samprate,sampwidth)
        elif type==TRIANGULAR_WAVE:
            gen = generate_triangular(frequency,seconds,volume,samprate,sampwidth)
        elif type==SQUARE_WAVE:
            gen = generate_square(frequency,seconds,volume,samprate,sampwidth)
        else:
            raise ValueError("Invalid wave type %d"%type)
        data = to_raw_data(gen,sampwidth,size) # 生成声波的字节数据
        wav_data = to_wav_data(data,samprate,sampwidth) # 构造wav文件
        #with open("test.wav","wb") as f:
        #    f.write(wav_data)
        if use_cache:_beep_cache[(frequency,duration,type)] = wav_data

    PlaySound(wav_data,SND_MEMORY) # 播放声音

def test_convert(filename="test.wav"):
    samprate = 11025;sampwidth = 1
    rate,width,seconds=get_wav_info(filename)
    size = int(samprate * seconds * sampwidth)
    wav=read_wav(filename)
    converted=convert(wav,rate,width,samprate,sampwidth)
    sound=adjust_volume(converted,sampwidth,0.3)
    data=to_raw_data(sound,sampwidth,size)
    wav_data=to_wav_data(data,samprate,sampwidth)
    PlaySound(wav_data,SND_MEMORY)

def test_white_noise():
    samprate = 44100;sampwidth = 2
    seconds = 1.8
    volume_db = -40
    volume = 1 * 10**(volume_db/20)
    size = int(samprate * seconds * sampwidth)
    gen=generate_white_noise(volume,seconds,samprate,sampwidth)
    data=to_raw_data(gen,sampwidth,size)
    wav_data=to_wav_data(data,samprate,sampwidth)
    PlaySound(wav_data,SND_MEMORY)
def test_red_noise(): # 生成红噪声，类似于风的声音
    samprate = 44100;sampwidth = 2
    seconds = 1.8
    volume_db = -20
    volume = 1 * 10**(volume_db/20)
    size = int(samprate * seconds * sampwidth)
    white=generate_white_noise(volume,seconds,samprate,sampwidth)
    gen=integral(white,volume,sampwidth)
    #view_freq_spectrum(gen,samprate,sampwidth);return # 一个生成器只能输出一次
    data=to_raw_data(gen,sampwidth,size)
    wav_data=to_wav_data(data,samprate,sampwidth)
    PlaySound(wav_data,SND_MEMORY)

def _instrument_sound(freq,decline=5):
    return [(SINE_WAVE,freq,0),
            (SINE_WAVE,freq*2,-decline),
            (SINE_WAVE,freq*3,-decline*2),
            (SINE_WAVE,freq*4,-decline*3)]
_sound2 = [(SINE_WAVE,450,0),
           (SINE_WAVE,850,-5),
           (SINE_WAVE,2500,-10)]
def test_mixed_sound(sounds):
    samprate = 44100;sampwidth = 2
    seconds = 1.8;volume=0.2
    size = int(samprate * seconds * sampwidth)
    gen=wave_mixer(sounds,seconds,volume,samprate,sampwidth)
    data=to_raw_data(gen,sampwidth,size)
    wav_data=to_wav_data(data,samprate,sampwidth)
    PlaySound(wav_data,SND_MEMORY)

def test():
    test_convert()
    Beep(220.5,1800,type=SINE_WAVE)
    Beep(220.5,1800,type=TRIANGULAR_WAVE)
    Beep(220.5,1800,type=SQUARE_WAVE)
    test_white_noise()
    test_red_noise()
    test_mixed_sound(_instrument_sound(220))
    test_mixed_sound(_sound2)

if __name__=='__main__':test()
