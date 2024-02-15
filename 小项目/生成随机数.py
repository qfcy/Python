import math
import matplotlib.pyplot as plt
from random import random as random2

class LinearCongruence:
    def __init__(self,seed,k,b,p):
        self.seed=seed
        self.k=k;self.b=b;self.p=p
    def random(self):
        self.seed = (self.seed*self.k + self.b) % self.p
        return self.seed

def count(lst,max_value,d):
    # 统计lst中每个范围内数值的出现次数,d为组距
    result=[0]*math.ceil(max_value/d) # ceil为向上取整
    for i in lst:
        result[int(i//d)]+=1
    return result

plt.rcParams['font.sans-serif'] = ['SimHei'] # 用于正常显示中文
seed = 1.7
k=5.6;b=3.5
p=1;d=0.001

l=[]
cnt=10000
lc=LinearCongruence(seed,k,b,p)
for j in range(cnt):
    l.append(lc.random())

# 绘制l从0至1的数值分布直方图，检验随机数的数值分布是否均匀
l=count(l,p,d)
plt.bar(range(len(l)),l)
plt.title("自制的线性同余算法")
plt.show()

l2=[random2() for i in range(cnt)]
# 绘制l2的数值分布直方图
l2=count(l2,p,d)
plt.bar(range(len(l2)),l2)
plt.title("Python内置random模块")
plt.show()
