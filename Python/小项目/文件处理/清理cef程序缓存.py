# 程序可用于清理常用软件如WPS、钉钉、Edge的缓存数据，适用于大多数软件
# 原理：自动识别CEF架构程序缓存的所在文件夹，并清理
import sys,os,shutil,traceback
import search_file

folders=["blob_storage","Cache","Code Cache","databases",
         "Local Storage","Service Worker","Session Storage"]
count = 0
for direc in search_file.direc("C:\\",files=False):
    try:
        flag=True
        for fd in folders:
            if not os.path.isdir(os.path.join(direc,fd)):
                flag=False
        if flag:
            print("清理",os.path.join(direc,"Cache"))
            shutil.rmtree(os.path.join(direc,"Cache"))
            print("清理",os.path.join(direc,"Service Worker\\CacheStorage"))
            shutil.rmtree(os.path.join(direc,"Service Worker\\CacheStorage"))
    except Exception:
        print("清理",direc,"出错")
        # 说明：清理某些软件缓存需要管理员权限
        traceback.print_exc()
    count+=1
    if count % 1000==0:
        print("已扫描",count,"个文件夹")

input("按Enter键继续 ..")