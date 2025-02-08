import os,time,search_file

for p in search_file.directories("E:\\python",dirs=False):
    t=os.stat(p).st_mtime
    tm=time.localtime(t)
    if (tm.tm_hour >=22 or tm.tm_hour <=3):
        print(p,tm.tm_mday,tm.tm_hour,tm.tm_min)
        os.utime(p,times=(t+3600*9,)*2)
