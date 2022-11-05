def f(n):
    r=""
    if n>0:
        r=r+str(n%2)
        return f(n//2)+r
    else:
        return r
