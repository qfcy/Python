import sys,os,time
# 时间最高支持 2108 01 01 (07:59:58)
format = "%Y %m %d"
time_ = input('输入 %s 格式的时间: '%format)
for arg in sys.argv[1:]:
    os.utime(arg,
             (time.mktime(time.strptime(time_, format)),)*2)
