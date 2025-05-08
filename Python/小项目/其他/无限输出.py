import sys
from random import randrange

def print(quiet=False,max=55296,file=sys.stdout):
    str=""
    for n in range(50):
        #每次输出一行
        char=chr(randrange(0,max)) # 生成随机字符
        if not char=='\x07' or not quiet:str+=char
    file.write(str)
def print_asciis(quiet=True):
    print(quiet=quiet,max=128)
def main():
    try:
        import colorama
        colorama.init()
    except ImportError:pass
    input("按Enter键开始无限输出 ...")
    while True:print(quiet=True)

if __name__=="__main__":main()
