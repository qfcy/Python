# 程序功能: 更新目标目录中的文件, 进行数据备份
import sys,os,shutil
from search_file import direc

def normpath(path):
    path=os.path.normpath(path).strip('"')
    if path.endswith(':'):
        path += '\\'
    return path
    
src = normpath(input('输入源目录: ')).strip('"').strip()
dst = normpath(input('输入目标目录: ')).strip('"').strip()
def copy2(src,dst):
    if not os.path.isdir(os.path.split(dst)[0]):
        os.makedirs(os.path.split(dst)[0],exist_ok=True)
    shutil.copy2(src,dst)

for file in direc(src,dirs=False):
    dst_file = dst + file.replace(src,'')
    if os.path.isfile(dst_file):
        # 用源目录中新的文件替换旧的文件
        if os.stat(file).st_mtime > os.stat(dst_file).st_mtime:
            print('已复制:',file,dst_file)
            copy2(file,dst_file)
        elif os.stat(file).st_mtime < os.stat(dst_file).st_mtime:
            # 目标目录中文件较新时
            ans=input('是否复制 %s 到 %s ? (Y/N)' % (dst_file,file))
            if ans.lower().startswith('y'):
                copy2(dst_file,file)
    else:
        # 旧文件不存在时, 直接复制
        print('已复制:',file,dst_file)
        copy2(file,dst_file)

# 删除目标目录中存在, 而源目录相同位置不存在的文件
all=False
for file in direc(dst,dirs=False):
    if not os.path.isfile(
        os.path.join(src, file.replace(dst,'').lstrip('\\'))):
        if all:
            print('已删除 '+file)
            os.remove(file)
        else:
            ans=input('删除 %s ? (Y/N/All)' % (file))
            if ans.lower().startswith('y'):
                os.remove(file)
            elif ans.lower() == 'all':
                all=True;os.remove(file)

if not 'pythonw' in os.path.split(sys.executable)[1]:
    os.system('pause')
