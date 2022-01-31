from time import perf_counter
l=[];t=[]
for i in range(1,9):
    s=perf_counter()
    with open("%d.py"%i,'rb') as f:
        d=f.read().decode()
    t.append(perf_counter()-s)
    l.append(d)
