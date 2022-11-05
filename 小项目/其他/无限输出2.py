from time import sleep
from random import choice
import colorama
colorama.init()

input("按Enter键开始无限输出 ...")
# 这样会使输出的文字随机变换颜色
charlist=["\033","[","m"]+[str(i) for i in range(1,10)]+[' ']*3
#charlist=[chr(i) for i in range()]
#charlist.remove('\a') # 去除振铃符号
while True:
    str=""
    for n in range(100):
        #每次输出一行
        char=choice(charlist) # 从charlist中选择一个随机字符
        str+=char
    print(str,end="")
    sleep(0.004)
