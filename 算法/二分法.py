import math

def getvalue(func,y,min,max):
    x = (min+max) / 2
    flag1=0.4;flag2=0.6
    while True:
        val = func(x)
        if func(min*flag1+max*flag2) > val:
            # 递增
            if val < y:
                min = x
            elif val > y:
                max = x
            elif math.isclose(y,val):
                return x
        elif func(min*flag1+max*flag2) < val:
            # 递减
            if val < y:
                max = x
            elif val > y:
                min = x
            elif math.isclose(y,val):
                return x
        else:
            flag1 = 0.25 + flag1 / 2
            flag2 = 0.25 + flag2 / 2
        x = (min+max) / 2
        print(min,max)

#print(getvalue(lambda x:-math.log10(x),-2,15,150))

def guess():
    value = 56
    def func(x):
        return x - value
    # 在0-100范围内, func(x)=100, 求x
    print(getvalue(func,0,0,100))

guess()
