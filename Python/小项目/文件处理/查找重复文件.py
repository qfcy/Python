import sys,os,traceback
from collections import defaultdict
#from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Process

def convert_bytes(num): # 将整数转换为数据单位
    units = ["", "K", "M", "G", "T", "P", "E", "Z", "Y"]

    for unit in units:
        if num < 1024:
            return f"{num:.2f}{unit}B"
        num /= 1024
    return f"{num:.2f}{units[-1]}B"

def walk(path):
    # 一个生成器, 列出path下的所有文件路径及大小。
    for root,_dirs,_files in os.walk(path):
        for name in _files:
            try:
                file=os.path.join(root, name)
                size=os.path.getsize(file)
                yield file,size
            except OSError as err:
                print("异常：%s"%file,file=sys.stderr)
                traceback.print_exc()

def compare_files(files, chunk_size=1 << 20):
    # 比较多个文件的内容，返回重复文件的字典
    opened_files = [open(file, 'rb') for file in files]
    file_count = len(opened_files)

    # 初始化重复文件字典，默认为True
    duplicates_dict = {(files[i], files[j]): True for i in range(file_count)\
                       for j in range(i + 1, file_count)}

    try:
        while True:
            chunks = [f.read(chunk_size) for f in opened_files]
            if not any(chunks):  # 如果所有文件都到达末尾
                break

            # 比较当前读取的块
            for i in range(file_count):
                for j in range(i + 1, file_count):
                    if duplicates_dict[(files[i], files[j])]:  # 只有在之前认为是重复的情况下才比较
                        if chunks[i] != chunks[j]:  # 如果块不一致
                            duplicates_dict[(files[i], files[j])] = False  # 更新为False

    finally:
        for f in opened_files:
            f.close()  # 确保文件在结束时关闭

    return duplicates_dict

def remove_duplicates(result):
    # 根据比较结果，删除重复文件
    renamed = set()
    for (file1, file2), is_duplicate in result.items():
        if is_duplicate and file2 not in renamed:
            print(f"找到重复文件：{file1}\n\t      {file2}")
            try:
                new_name = file2 + "._deleted"
                os.rename(file2, new_name)
                renamed.add(file2)
            except Exception as e:
                print(f"重命名失败: {file2} - {e}", file=sys.stderr)

def restore(path,extension="._deleted"):
    # 备用函数，恢复被重命名的文件
    for root,_dirs,_files in os.walk(path):
        for name in _files:
            if name.lower().endswith(extension):
                filename=os.path.join(root,name)
                os.rename(filename,os.path.join(root,name[:-len(extension)]))
                print("恢复文件:",filename)

def process_size_dict(size_dict):
    for size, files in size_dict.items():
        files.sort(key=lambda file:\
                   os.path.splitext(os.path.split(file)[1])[0]) # 按文件名升序排序
        result=compare_files(files)
        remove_duplicates(result)

def process_size_dict_thread(size_dict):
    try:
        process_size_dict(size_dict)
    except Exception:
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv)==2:
        path=sys.argv[1]

        # 预处理，找出相同大小的文件并分组
        print("解析目录 ...")
        size_dict = defaultdict(list)
        for file, size in walk(path):
            size_dict[size].append(file)
        # 去除单个的文件
        size_dict={size:files for size,files in size_dict.items() if len(files)>1}

        # 处理重复文件
        total=sum(size*len(files) for size,files in size_dict.items()) # 计算总大小
        print("解析成功，发现 %d 组文件，总大小 %s"%(len(size_dict),convert_bytes(total)))
        cpus=os.cpu_count() # 线程数
        expected_size=total/cpus
        size_dicts=[]
        cur={};tot=0
        for size, files in size_dict.items(): # 为每个线程分配合适的任务量
            cur[size]=files
            tot+=size*len(files)
            if tot>=expected_size:
                size_dicts.append(cur)
                cur={};tot=0
        if cur:
            size_dicts.append(cur)

        print("处理重复文件，进程数: %d ..."%len(size_dicts))
        # 单线程: process_size_dict(size_dict)
        # 多线程，经测试发现无法避开GIL锁
        #with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        #    for task in size_dicts:
        #        executor.submit(process_size_dict_thread, task)
        # 多进程
        processes = []
        for task in size_dicts:
            p = Process(target=process_size_dict_thread,args=(task,))
            p.start()
            processes.append(p)
        for p in processes: # 等待所有进程结束
            p.join()
    else:
        print("用法: %s <要查找重复文件的路径>"%sys.argv[0])