import os
import importlib as __imp

def __import_mod(fmt_str="painter.%s"):
    # 自动搜索最高版本的模块，并导入
    path=os.path.split(__file__)[0]
    versions=[]
    for file in os.listdir(path):
        split_ext=os.path.splitext(file)
        if split_ext[1].lower()==".py":
            ver=split_ext[0]
            versions.append(ver)
    # 仅适用于版本号数字的范围均为0-9
    versions.sort(reverse=True) # 降序
    for ver in versions:
        #exec("from painter.%s import Painter,main"%ver)
        module=__imp.__import__(fmt_str%ver)
        print("Painter %s"%ver)
        return getattr(module,ver,module)
    return None

try:
    mod=__import_mod()
    if not mod:raise ImportError("Could not find module painter.vx_x")
    scope=globals()
    #相当于from xxmodule import *
    for attr in dir(mod):
        scope[attr]=getattr(mod,attr,None)

    del mod,scope,attr
except ImportError:pass
