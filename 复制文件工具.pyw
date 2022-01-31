#功能:根据关键词, 静默复制文件到一个目录
import sys,os,time,traceback
from shutil import copyfile

__ver__='1.3.2'

sys.stderr=open("debug.log","w",encoding='utf-8')
print("--程序启动于: %s --"%time.asctime())
with open("config.ini") as f:
    # config.ini 第一行为源目录, 第二行为目标目录, 用";"分隔
    # 之后每一行为一个关键词
    paths=[os.path.realpath(p) for p in f.readline().strip().split(';')]
    dsts=[os.path.realpath(p) for p in f.readline().strip().split(';')]
    words=f.read().splitlines()

for dst in dsts:
    try:os.mkdir(dst)
    except FileExistsError:pass
    except Exception:
        traceback.print_exc()

def check_key(str,words):
    # 检查关键词是否在文件名中
    str=str.lower()
    for w in words:
        if w.lower() in str:return True
    return False

def run():
    for path in paths:
        if not os.path.isdir(path):
            print("路径 %s 不存在"%path,file=sys.stderr)
            continue
        os.chdir(path)
        for filename in os.listdir("."):
            if check_key(filename,words):
                for dst in dsts:
                    # 目标文件不存在
                    if not os.path.isfile(
                        os.path.join(dst,filename)):
                        try:
                            copyfile(os.path.join(path,filename),
                                     os.path.join(dst,filename))
                            sys.stderr.write("复制文件%s 到 %s\r\n"%(filename,dst))
                        except Exception:
                            traceback.print_exc()

while True:
    try:
        run()
    except Exception:
        traceback.print_exc()
    sys.stderr.flush()
    time.sleep(1)
