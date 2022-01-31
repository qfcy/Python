import sys,os,time
level=int(sys.argv[1]) if len(sys.argv)==2 else 1
print("层级 %d 开始运行"%level)
version=sys.winver.replace('.','')
start=time.perf_counter()
os.system('{} "{}" {}'.format(
    sys.executable,sys.argv[0],level+1))
print("层级 %d 结束 耗时:%f秒"%(level,time.perf_counter()-start))