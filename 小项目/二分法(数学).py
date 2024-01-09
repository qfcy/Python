import math

PRECISION=1e-15 # 浮点比较精度
def getvalue(func,y,min,max):
    start_min=min; start_max=max
    flag1=0.4; flag2=0.6 # 用于判断递增和递减
    max_iter=200; cnt=0
    x = (min + max) / 2
    while cnt < max_iter:
        val = func(x)
        if func(min*flag1+max*flag2) > val:
            # 递增时
            if math.isclose(y,val,rel_tol=PRECISION): # 判断两个浮点数是否接近，这里不能用"=="
                print("查找次数:",cnt+1)
                return x
            elif val < y:
                min = x # 右移
            else:
                max = x # 左移
        elif func(min*flag1+max*flag2) < val:
            # 递减时
            if math.isclose(y,val):
                print("查找次数:", cnt + 1)
                return x
            elif val > y:
                min = x # 右移
            else:
                max = x # 左移
        else:
            flag1 = 0.25 + flag1 / 2 # 减小flag1, flag2之间的差
            flag2 = 0.25 + flag2 / 2
        x = (min+max) / 2
        print("min:",min,"max:",max,"val:",val)
        cnt += 1
    # 达到了最大次数，仍未找到结果
    if math.isclose(max,start_min,rel_tol=PRECISION):
        print("结果应小于最小值 (%d)"%start_min)
    elif math.isclose(min,start_max,rel_tol=PRECISION):
        print("结果应大于最大值 (%d)"%start_max)
    else:
        print("精度设定值可能过小")
#print(getvalue(lambda x:-math.log10(x),-2,15,150))

def guess():
    k=1.5 ; b=1
    def func(x):
        return k*x + b
    # 在0-100范围内, func(x)=150, 求x
    print("结果:",getvalue(func,150,0,100))

if __name__=="__main__":guess()
