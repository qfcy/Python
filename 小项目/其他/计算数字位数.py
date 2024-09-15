import sys,math
while True:
    try:
        result=input("输入一个数:")
        n=abs(float(result))
    except ValueError:
        if result.strip():
            print("%r is not a number.Try again."%result,file=sys.stderr)
        continue
    if n==0:
        w=1
    else:
        w=math.floor(math.log10(n)+1)#计算位数
        if w<=0:w=-w+2
    print("位数:"+str(w))
