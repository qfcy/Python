import sys,os,time

__all__=["directories","direc","search"]
__email__="3076711200@qq.com"
__author__="七分诚意 qq:3076711200"
__version__="1.2.2"

def dir(path):
    for dir_entry in os.scandir(path):
        yield dir_entry.path

def directories(path,dirs=True,files=True):
    """一个生成器, 列出path下的所有子目录和文件名。
如:
>>> from search_file import directories
>>> list(directories("C:\\"))
['C:\\Users',  #第一层目录
'C:\\Users\\Administrator', #第二层目录
...,
'C:\\Windows',
'C:\\Windows\\System32',
...]
dirs: 是否列出目录
files: 是否列出文件
"""
    for root,_dirs,_files in os.walk(os.path.realpath(path)):
        if dirs:
            for name in _dirs:
                yield os.path.join(root, name)
        if files:
            for name in _files:
                yield os.path.join(root, name)

direc=directories #定义别名

def search(filename,path,minsize=None,maxsize=None):
    """一个生成器,在path中搜索一个文件或文件夹。
如:
>>> from search_file import search
>>> list(search("cmd.exe","C:\\"))
['C:\\Windows\\System32\\cmd.exe',
...]"""
    for file in directories(path):
        if filename in file:
            size=os.path.getsize(file)
            if (size>=minsize if minsize is not None  else True)\
               and (size<=maxsize if maxsize is not None  else True):
                yield file

def test():
    "找出目录(默认为系统盘)中的大文件。"
    print("搜索大文件中 ...")
    start_time=time.perf_counter()
    min_size=2**27 # 128MB
    files=[]
    dir=sys.argv[1] if len(sys.argv)>1 else os.environ.get("systemdrive")
    for path in directories(dir,dirs=False):
        if os.path.isfile(path):
            size=os.path.getsize(path)
            if size>=min_size:
                print("找到文件:{} ({:.2f}MB)".format(path,size/(2**20)))
                files.append(path)
    largest_file = max(files,key=os.path.getsize)
    print("最大的文件: %s (%fGB)"%(
        largest_file,os.path.getsize(largest_file)/(2**30)))
    print("用时:{:2f}秒".format(time.perf_counter()-start_time))

if __name__=="__main__":test()
