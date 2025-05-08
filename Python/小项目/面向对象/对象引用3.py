def f():pass
old_f=f
l=[];first=True
while True:
    try:
        l.append(f) # 这一步内存会被无限占用
        f=f.__call__
    except MemoryError:
        if first:
            print('MemoryError',len(l))
            first=False
