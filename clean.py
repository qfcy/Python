# 清除空文件夹的工具
import sys,os
from logging import basicConfig,log,INFO
from search_file import direc

__ver__="1.4"
# --files:只删除空文件
# --dirs:只删除空文件夹
basicConfig(filename="delete.log",level=INFO)
del_dirs=not '--files' in sys.argv or '--dirs' in sys.argv
del_files=not '--dirs' in sys.argv or '--files' in sys.argv

dir=sys.argv[1] if len(sys.argv)>1 and not sys.argv[1].startswith("-") else "C:\\"
deleted_files=[]
for path in direc(dir):
    try:
        if not "windows" in path.lower():
            if os.path.isfile(path):
                if del_files and os.path.getsize(path)==0:
                    print("删除文件: %s"%path)
                    log(INFO,"删除文件: %s"%path)
                    os.remove(path)
                    deleted_files.append(path)
            elif del_dirs and not os.listdir(path):
                print("删除空文件夹: %s"%path)
                log(INFO,"删除文件: %s"%path)
                os.removedirs(path)
                deleted_files.append(path)
    except Exception as err:
        print(err,file=sys.stderr)

print("\n共删除空文件和空文件夹 %d 个"%len(deleted_files))
if 0<len(deleted_files)<20:
    print("删除的文件和目录:")
    for file in deleted_files:
        print(file)
