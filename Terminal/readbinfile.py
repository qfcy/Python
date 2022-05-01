#读取二进制文件的程序
import sys,os,colorama

__email__="3416445406@qq.com"
__author__="fufvocdi 邮箱:%s"%__email__
__version__="1.0"

def readbinfile(filename):
    "读取一个二进制文件,并打印出该文件的内容。"
    f=open(filename,"rb")
    while True:
        byte=f.read(1)
        if not byte:break
        #如果该字符为数字或字母
        if b'0'<=byte<=b'9' or b'a'<=byte<=b'z' or b'A'<=byte<=b'Z':
             #直接打印出这个字符,颜色为绿色
            print('[1m[32m%s[0m'%str(byte,encoding="utf-8"),end='')
        elif b' '<byte<b'\x7f':
            print(str(byte,encoding="utf-8"),end='')
        else:print(ord(byte),end=" ") #打印出字符的ASCII码

if __name__=="__main__":
    colorama.init() #初始化colorama模块,以打印出彩色文本
    if len(sys.argv)>1:filename=sys.argv[1]
    else:filename=input("拖曳文件到本窗口,然后按回车:\n")

    if filename.strip():
        os.system("title readbinfile - %s"%filename) #设置命令行窗口标题
        readbinfile(filename)
        input()
