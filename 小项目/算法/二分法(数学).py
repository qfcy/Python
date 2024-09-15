import math

PRECISION=1e-15 # 函数值的浮点比较精度
def getvalue(func,y,min,max):
    start_min=min; start_max=max
    rate1=0.4; rate2=0.6#0.7 # 用于判断单调性(递增和递减)
    max_iter=200; cnt=0
    while cnt < max_iter:
        x = (min+max) / 2
        val = func(x)
        val2 = func(min*rate1+max*rate2) # 在x附近取点，用于判断x附近的单调性
        print("min:",min,"max:",max,"val:",val)
        if val2 > val:
            # 递增时
            if math.isclose(y,val,rel_tol=PRECISION): # 判断两个浮点数是否接近，这里不能用"=="
                print("查找次数:",cnt+1)
                return x
            elif val < y:
                min = x # 右移
            else:
                max = x # 左移
        elif val2 < val:
            # 递减时
            if math.isclose(y,val):
                print("查找次数:", cnt + 1)
                return x
            elif val > y:
                min = x # 右移
            else:
                max = x # 左移
        else: # 调整rate1和rate2，再次判断单调性
            rate1 = 0.25 + rate1 / 2 # 减小rate1, rate2之间的差，使取点更接近x
            rate2 = 0.25 + rate2 / 2
        cnt += 1
    # 达到了最大次数，仍未找到结果
    if math.isclose(max,start_min,rel_tol=PRECISION):
        print("结果应小于最小值 (%d)"%start_min)
    elif math.isclose(min,start_max,rel_tol=PRECISION):
        print("结果应大于最大值 (%d)"%start_max)
    else:
        print("精度设定值可能过小")

def guess():
    def func(x):
        return x ** 2
    # 在0-10范围内, func(x)=10, 求x
    print("结果:",getvalue(func,10,0,10))

if __name__=="__main__":guess()
