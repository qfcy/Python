import timer_tool,math
s=float(input("输入s(x**x=s): "))
t=timer_tool.Timer() # 开始计时
# 法一（实测证明s>=e**e (x>=e(≈2.71828))时计算会较慢）
x=1;cnt=0
while True:
    x=s ** (1/x) # 相当于 x=x√(s)
    cnt+=1
    if math.isclose(x**x,s):
        break
# 法二：二分法（详见 二分法(数学).py）

time=t.gettime()
print("x=",x,"x**x=",x**x)
print("迭代次数:",cnt,"用时(秒):",time,"每次迭代平均用时(秒):",time/cnt)