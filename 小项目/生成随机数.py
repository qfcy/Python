import matplotlib.pyplot as plt
from time import perf_counter
from random import random as random2

seed = perf_counter()
k=5.6;b=3.5
i=1
def random():
    global seed
    seed=seed*k+b
    if seed > 10**10:
        seed=perf_counter() # 加入时间的随机因素
    return seed % i

l=[]
for j in range(500):
    l.append(random())
    k=random()*5.6 # 变化k, 避免随机数重复

#pprint(l)
plt.hist(l,bins=len(l)//5)
plt.show()

l2=[random2() for i in range(500)]
plt.hist(l2,bins=len(l2)//5)
plt.show()
