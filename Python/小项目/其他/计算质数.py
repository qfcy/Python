import math

def prime(num):
    if num<=0:
        raise ValueError("数值必须大于0")
    elif num==1:
        return False # 1既不是质数也不是合数
    for i in range(2,int(math.sqrt(num))+1):
        if num%i==0:
            return False

    return True

num=int(input("输入数: "))
print(("%s是质数" if prime(num) else "%d不是质数") % num)