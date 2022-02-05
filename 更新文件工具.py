# 程序功能: 更新目标目录中的文件, 进行数据备份
# 用途: 包含大量文件的文件夹的备份, 解决备份文件夹时
# 需要复制整个文件夹的问题
import sys,os,shutil,fnmatch,traceback
from search_file import direc

def normpath(path):
    path=os.path.normpath(path).strip('"')
    if path.endswith(':'):
        path += '\\'
    return path

def copy2(src,dst):
    if not os.path.isdir(os.path.split(dst)[0]):
        os.makedirs(os.path.split(dst)[0],exist_ok=True)
    shutil.copy2(src,dst)

def read_ig(ignore_listfile): # 读取忽略文件列表
    l=[]
    with open(ignore_listfile,encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line[0] not in ('$','#'): # 忽略注释
                l.append(line)
    return l

def check_ig(file, ignore_list): # 判断文件是否应被忽略
    for ig in ignore_list:
        if fnmatch.fnmatch(file,ig):
            return True
    return False

def main():
    if len(sys.argv) >= 3:
        src,dst = sys.argv[1:3]
        ignore_listfile = sys.argv[3] if len(sys.argv) >= 4 else None
    else:
        print('用法:%s <源目录> <目标目录>'%sys.argv[0])
        src = normpath(input('输入源目录: ')).strip('"').strip()
        dst = normpath(input('输入目标目录: ')).strip('"').strip()
        default = '.gitignore'
        ignore_listfile = normpath(input('忽略的文件列表 (默认 %s): '%default)
                                   or default).strip('"').strip()

    if ignore_listfile is not None:ignore_list = read_ig(ignore_listfile)
    else:ignore_list = []

    all_=False;ignore_all=False
    for file in direc(src,dirs=False):
        print(check_ig(file, ignore_list))
        if check_ig(file, ignore_list):continue

        dst_file = dst + file[len(src):] # 原为file.replace(src,'')
        if os.path.isfile(dst_file):
            # 用源目录中新的文件替换旧的文件
            if os.stat(file).st_mtime > os.stat(dst_file).st_mtime:
                print('已复制:',file,dst_file)
                copy2(file,dst_file)
            elif os.stat(file).st_mtime < os.stat(dst_file).st_mtime:
                # 目标目录中文件较新时

                if all_:
                    copy2(dst_file,file)
                elif not ignore_all:
                    ans=input('是否复制 %s 到 %s ? [Y/N/A(All)/I(Ignore all)]'\
                              % (dst_file,file))
                    if ans.lower().startswith('y'):
                        copy2(dst_file,file)
                    elif ans.lower() in ('a','all'):
                        all_=True;copy2(dst_file,file)
                    elif ans.lower() in ('i','ignore all'):
                        ignore_all=True
                else:
                    print('忽略 %s'%dst_file)
        else:
            # 旧文件不存在时, 直接复制
            print('已复制:',file,dst_file)
            copy2(file,dst_file)

    # 删除目标目录中存在, 而源目录相同位置不存在的文件
    all_=False;ignore_all=False
    for file in direc(dst,dirs=False):
        if check_ig(file, ignore_list):continue

        if not os.path.isfile(
            os.path.join(src, file[len(dst):].lstrip('\\'))):
            if all_:
                print('已删除 '+file)
                os.remove(file)
            elif not ignore_all:
                ans=input('删除 %s ? [Y/N/A(All)/I(Ignore all)]' % (file))
                if ans.lower().startswith('y'):
                    os.remove(file)
                elif ans.lower() in ('a','all'):
                    all_=True;os.remove(file)
                elif ans.lower() in ('i','ignore all'):
                        ignore_all=True
            else:
                print('忽略 %s'%file)

    # 删除目标目录中存在, 而源目录不存在的空目录
    for dir_ in direc(dst,files=False):
        if check_ig(dir_, ignore_list):continue

        if not os.listdir(dir_)\
    and not os.path.isfile(os.path.join(src, dir_[len(dst):].lstrip('\\'))):
            os.removedirs(dir_)
            print('已删除空目录 %s'%dir_)


if __name__=="__main__":
    try:main()
    except Exception: #目的是避免异常时程序闪退
        traceback.print_exc()
    if not 'pythonw' in os.path.split(sys.executable)[1]:
        os.system('pause')
