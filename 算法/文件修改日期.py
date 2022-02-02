import sys,os,time
for arg in sys.argv[1:]:
    os.utime(arg,
             (time.mktime(time.strptime("2108 01 01 07:59:58", "%Y %m %d %H:%M:%S")),)*2)
