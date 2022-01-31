def f():pass
old_f=f
l=[];first=True
while True:
    try:
        l.append(f)
        f=f.__call__
    except MemoryError:
        if first:
            print('MemoryError',len(l))
            first=False
