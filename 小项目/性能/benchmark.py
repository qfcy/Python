import time,os

files=30
s=time.perf_counter()
for i in range(files):
    open(str(i),'wb').close()
print('创建文件',time.perf_counter()-s)

s=time.perf_counter()
for i in range(files):
    os.remove(str(i))

print('删除文件',time.perf_counter()-s)
input()
