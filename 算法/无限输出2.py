from time import sleep
from random import choice
import colorama
colorama.init()

input("按Enter键开始无限输出 ...")
charlist=["\033","[","m"]+[str(i) for i in range(1,10)]+[' ']*3
#charlist=[chr(i) for i in range()]
#charlist.remove('\a')
while True:
    str=""
    for n in range(100):
        #每次输出一行
        char=choice(charlist)
        str+=char
    print(str,end="")
    sleep(0.004)
