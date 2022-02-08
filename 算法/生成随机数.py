import matplotlib.pyplot as plt
from time import perf_counter
from pprint import pprint

seed = perf_counter()
k=5.6;b=3.5
i=1
def random():
    global seed
    seed=seed*k+b
    if seed > 10**10:
        seed=perf_counter()
    return seed % 1

l=[]
for i in range(500):
    l.append(random())
    k=random()*5.6

#pprint(l)
plt.hist(l,bins=len(l)//5)
plt.show()
