from random import *

def GetRandomChar():

    # GetRandomChar()返回一个字符, 而不是字符串

    while True:

        a=randint(48,122)

        if not 58<=a<=64 and not 91<=a<=96:return chr(a)



m=eval(input("请输入一个整数:"))

if m<5 or m>10:

    print("请输入5-10之间的整数")

else:

    s=""

    for i in range(m):

        s+=GetRandomChar()

    print("验证码为"+s)
