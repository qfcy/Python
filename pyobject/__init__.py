"""一个关于Python对象工具的模块。
A tool of python object with tkinter and command-lines.

"""

import sys
from pprint import pprint

__email__="3416445406@qq.com"
__author__="七分诚意 qq:3076711200 邮箱:%s"%__email__
__version__="1.2.0"

_ignore_names=["__builtins__","__doc__"]
__all__=["objectname","bases","describe","desc",
         "browse","make_list","search"]

def objectname(obj):
    """objectname(obj) - 返回一个对象的名称,形如xxmodule.xxclass。
如:objectname(int) -> 'builtins.int'"""
    if not obj.__class__==type:obj=obj.__class__
    if obj.__module__=="__main__":return obj.__name__
    return "{}.{}".format(obj.__module__,obj.__name__)

###无递归版本
##def base(obj):
##    while True:
##        try:
##            obj=obj.__bases__
##        except AttributeError:obj=[obj.__class__]
##        if not obj:break
##        else:obj=obj[0]
##        print(obj)
def bases(obj,level=0,tab=4):
    '''bases(obj) - 打印出该对象的基类
tab:缩进的空格数,默认为4。'''
    if not obj.__class__==type:obj=obj.__class__
    if obj.__bases__:
        if level:print(' '*(level*tab),end='')
        print(*obj.__bases__,sep=',')
        for cls in obj.__bases__:
            bases(cls,level,tab)
        

def _shortrepr(obj,maxlength=150):
    result=repr(obj)
    if len(result)>maxlength:
        return result[:maxlength]+"..."
    return result

###无递归
##def describe(obj,verbose=True,needhelp=False,**kwargs):
##    "Prints the properties of an object."
##    __builtins__.print(repr(obj)+" :",**kwargs)
##    for attr in dir(obj):
##        if verbose or not attr.startswith("_"):
##            if not attr in ignore_names:
##                value=getattr(obj,attr)
##                pprint("{}:{}".format(attr,value),**kwargs)
##                if needhelp:help(value)
def describe(obj,level=0,maxlevel=1,tab=4,verbose=False,file=sys.stdout):
    '''"描述"一个对象,即打印出对象的各个属性。
参数说明:
maxlevel:打印对象属性的层数。
tab:缩进的空格数,默认为4。
verbose:一个布尔值,是否打印出对象的特殊方法(如__init__)。
file:一个类似文件的对象。
'''
    if level==maxlevel:
        result=repr(obj)
        if result.startswith('[') or result.startswith('{'):pprint(result)
        else:print(result,file=file)
    elif level>maxlevel:raise ValueError(
        "Argument level is larger than maxlevel")
    else:
        print(_shortrepr(obj)+': ',file=file)
        if type(obj) is type:
            print("Base classes of the object:",file=file)
            bases(obj,level+1,tab)
            print(file=file)
        for attr in dir(obj):
            if verbose or not attr.startswith("_"):
                print(' '*tab*(level+1)+attr+': ',end='',file=file)
                try:
                    if not attr in _ignore_names:
                        describe(getattr(obj,attr),level+1,maxlevel,
                                tab,verbose,file)
                    else:print(_shortrepr(getattr(obj,attr)),file=file)
                except AttributeError:
                    print("<AttributeError!>",end='',file=file)

desc=describe #别名
try:
    from .browser import *
# (ImportError,SystemError): 修复Python 3.4的bug
except (ImportError,SystemError):pass
try:
    from .search import make_list,search #,test_make_list,test_search
# 同上
except (ImportError,SystemError):pass

try:
    from .code_ import Code
except (ImportError,SystemError):pass

def test():
    try:
        describe(type,verbose=True)
    except BaseException as err:
        print("STOPPED!",file=sys.stderr)
        if not type(err) is KeyboardInterrupt:raise
        return 1
    else:return 0

if __name__=="__main__":sys.exit(test())
