# 无限地运行程序自身, 运行后, 打开任务管理器, 就会出现许多个python.exe
import sys,os,time,subprocess
if len(sys.argv)==3: # 被上一层调用执行
    level,t1=int(sys.argv[1]),float(sys.argv[2])
    t2 = time.time()
    print("层级 %d 开始运行, 距上一个层级开始 %.4f 秒" % (level,t2-t1))
else: # 直接执行
    level=1
    t2 = time.time()
    print("层级 1 开始运行")

# 方法1, 不过也会调用cmd.exe
# os.system('{} "{}" {} {}'.format(
#     sys.executable,sys.argv[0],level+1,t2))

# 方法2
subprocess.run([sys.executable,sys.argv[0],str(level+1),str(t2)])

print("层级 %d 结束, 本层级总耗时 %.4f 秒"%(level,time.time()-t2))