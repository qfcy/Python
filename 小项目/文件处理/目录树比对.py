import sys,os,warnings

def parse_directory_tree(filename):
    """
    解析目录树的字符串表示，返回嵌套字典。

    :param filename: 目录树所在的文件名。
    :return: 嵌套字典，表示目录结构。
    """
    root = current = {}
    stack = [root]
    with open(filename,encoding="utf-8") as f:
        for line in f:
            # 计算缩进级别
            line=line.strip()
            if not line:continue
            depth=line.count("├")+line.count("│")
            trimmed_line=line[depth*4:]
            #print(line,depth,trimmed_line)
            #raise

            # 导航到正确的深度
            while len(stack) > depth:
                stack.pop()
            current=stack[-1]

            # 创建当前目录或文件
            current[trimmed_line] = {}
            stack.append(current[trimmed_line])

    return root

def _get_local_directory_structure(path,struct):
    # 不使用os.chdir的实现
    #for sub in os.listdir(path):
    #    subdirs={}
    #    subpath=os.path.join(path,sub)
    #    if os.path.isdir(subpath):
    #        _get_local_directory_structure(subpath,subdirs)
    #    struct[sub]=subdirs
    pre_dir=os.getcwd()
    os.chdir(path) # 切换到当前路径
    try:
        for sub in os.listdir():
            subdirs={}
            if os.path.isdir(sub):
                _get_local_directory_structure(sub,subdirs)
            struct[sub]=subdirs
    except OSError as err:
        warnings.warn("无法获取目录结构：%s (%s: %s)" % (
            os.getcwd(),type(err).__name__,str(err)))
    os.chdir(pre_dir) # 恢复之前的目录
def get_local_directory_structure(path):
    """
    获取本地目录的嵌套字典结构。

    :param path: 本地目录路径。
    :return: 嵌套字典，表示本地目录结构。
    """
    struct={}
    pre_dir=os.getcwd()
    os.chdir(path)
    _get_local_directory_structure(path,struct)
    os.chdir(pre_dir)
    return struct

def compare_directories(expected, actual, path=""):
    """
    比较两个目录结构，找出缺失的和多余的文件。

    :param expected: 期望的目录结构（解析后的目录树）。
    :param actual: 实际的目录结构（本地目录）。
    :param path: 当前比较的路径（用于递归）。
    :return: 缺失的文件和多余的文件列表。
    """
    missing_files = []
    extra_files = []

    # 比较期望的目录结构与实际目录结构
    for key in expected:
        expected_path = f"{path}/{key}" if path else key

        if key not in actual:
            # 如果期望的文件/目录不在实际目录中
            missing_files.append(expected_path)
        else:
            # 如果是目录，递归比较
            if isinstance(expected[key], dict):
                sub_missing, sub_extra = compare_directories(expected[key], actual[key], expected_path)
                missing_files.extend(sub_missing)
                extra_files.extend(sub_extra)

    # 检查实际目录中多余的文件
    for key in actual:
        actual_path = f"{path}/{key}" if path else key

        if key not in expected:
            # 如果实际的文件/目录不在期望目录中
            extra_files.append(actual_path)

    return missing_files, extra_files

# Usage
if __name__ == "__main__":
    if len(sys.argv)==3:
        directory_tree_file = sys.argv[1]  # Change to your directory tree file path
        directory = sys.argv[2]          # Change to your local directory path

        print("解析目录树 ...")
        directory_tree=parse_directory_tree(directory_tree_file)
        print("解析本地路径 ...")
        local_directory=get_local_directory_structure(directory)
        print("比较中 ...")
        missing, extra = compare_directories(directory_tree, local_directory)

        with open("missing.txt","w",encoding="utf-8") as f: # 本地目录中缺失的文件
            for file in missing:
                print(file,file=f)

        with open("extra.txt","w",encoding="utf-8") as f:  # 本地目录中多余的文件
            for file in extra:
                print(file,file=f)
    else:
        print("用法: %s <目录树文件> <要对比的本地路径>"%sys.argv[0])