# 通过不断申请内存，测试计算机的可用内存极限值

def convert_size(num):
    suffix = ['B', 'KB', 'MB', 'GB', 'TB']
    index = 0
    while num >= 1024 and index < len(suffix) - 1:
        num /= 1024
        index += 1
    return f'{round(num, 3)} {suffix[index]}'

level = 30 # 2**30
lst=[]
total_mem = 0
while True:
    try:
        memsize = 2**level
        lst.append("s"*memsize)
        total_mem += memsize
        print("已申请内存：%d" % total_mem)
    except MemoryError:
        level -= 1
        if level < 0:break

print("程序退出，最大可申请内存：%s" % convert_size(total_mem))