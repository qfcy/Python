"提供查找、搜索python对象的函数的模块。"
import traceback,builtins,sys
from warnings import warn
try:
    from types import WrapperDescriptorType,MethodWrapperType,\
        MethodDescriptorType,ClassMethodDescriptorType,ModuleType
except ImportError: # 低于3.7的版本
    from types import ModuleType
    from typing import WrapperDescriptorType,MethodWrapperType,\
        MethodDescriptorType
    ClassMethodDescriptorType = type(dict.__dict__['fromkeys'])

__all__=["make_list","make_iter","search"]
_skip=(WrapperDescriptorType, MethodWrapperType,\
     MethodDescriptorType, ClassMethodDescriptorType) #自动忽略这些类型, 加快速度

# 重写Python的内置函数dir
def dir(obj):
    attrs=builtins.dir(obj)
    # __bases__属性一般不会出现在dir()的返回值中
    if hasattr(obj,"__bases__") and "__bases__" not in attrs:
        attrs.append("__bases__")
    return attrs

def _list_in(obj,lst):
    return obj in lst
try:
    from pyobj_extension import list_in as _list_in # 使用更高效的C扩展函数替代
except ImportError:
    warn("Failed to import module pyobj_extension.")
def _make_list(start_obj,recursions,lst,called,all=False,show_error=True):
    if recursions<=0:return

    if start_obj in called:return # 如果已经遍历过
    called.append(start_obj) # 将对象标记为已调用
    for attr in dir(start_obj):
        if all or not attr.startswith("_"):
            try:
                obj=getattr(start_obj,attr)
                if not _list_in(obj,lst):lst.append(obj)
                if obj.__class__ not in _skip:
                    _make_list(obj,recursions-1,lst,called,all,show_error)
            except Exception: # getattr()可能会返回AttributeError等异常
                if show_error:traceback.print_exc()
    if isinstance(start_obj,(list,tuple)):
        for item in start_obj:
            if not _list_in(item,lst):lst.append(item)
            if obj.__class__ not in _skip:
                _make_list(item,recursions-1,lst,called,all,show_error)
    if isinstance(start_obj,dict):
        for obj in start_obj.keys():
            if not _list_in(obj,lst):lst.append(obj)
        for obj in start_obj.values():
            if not _list_in(obj,lst):lst.append(obj)
            if obj.__class__ not in _skip:
                _make_list(obj,recursions-1,lst,called,all,show_error)

def make_list(start_obj,recursions=3,all=False,show_error=True):
    """创建一个包含大量对象的列表。
start_obj:开始搜索的对象。
recursions:最大递归层数，最小为1层。
all:是否将对象的下划线开头属性(如__init__)加入列表。
show_error:在getattr()内发生异常时，是否将异常输出至sys.stderr。"""
    lst=[];called=[]
    _make_list(start_obj,recursions,lst,called,all,show_error)
    return lst

def _make_iter(start_obj,recursions,called,all=False,show_error=True):
    if recursions<=0:return

    if start_obj in called:return # 如果已经遍历过
    called.append(start_obj) # 将对象标记为已调用
    for attr in dir(start_obj):
        if all or not attr.startswith("__"):
            try:
                obj=getattr(start_obj,attr)
                yield obj
                # 跳过method_wrapper类型
                # 经测试, 使用obj.__class__比使用type(obj)更快
                if obj.__class__ not in _skip:
                    for obj in _make_iter(obj,recursions-1,called,all,show_error):
                        yield obj
            except Exception:
                if show_error:traceback.print_exc()
    if isinstance(start_obj,(list,tuple)):
        for item in start_obj:
            yield item
            if item.__class__ not in _skip:
                for obj in _make_iter(obj,recursions-1,called,all,show_error):
                    yield obj
    if isinstance(start_obj,dict):
        for obj in start_obj.keys():
            yield obj
        for obj in start_obj.values():
            yield obj
            if obj.__class__ not in _skip:
                for o in _make_iter(obj,recursions-1,called,all,show_error):
                    yield o

def make_iter(start_obj,recursions=3,all=False,show_error=True):
    """创建一个对象的迭代器, 功能、参数与make_list相同, 
make_iter创建的迭代器可能会返回重复的对象, 而make_list不会。
"""
    called=[]
    for obj in _make_iter(start_obj,recursions,called,all,show_error):
        yield obj


def _search(target,start_obj,recursions,search_str=False,\
            verbose=True,cache=None,show_error=True):
    if recursions<=0:return []
    try:
        if cache and start_obj in cache: # 参数cache为字典或None
            return cache[start_obj] # 返回缓存中的结果
    except TypeError:pass # 某些类型如列表等无法作为字典键使用
    search_str=search_str and isinstance(target,str) # 如果启用搜索子串，则target必须是字符串
    results=[]
    for attr in dir(start_obj):
        if not verbose and attr.startswith("_"):
            continue
        try:
            name="." + attr
            if search_str and target in attr: # 搜索字符串的子串
                results.append(name)
            obj=getattr(start_obj,attr)
            if target==obj: # ==是为了处理数字、字符串等对象
                results.append(name)
                # 找到对象之后，仍然从该对象继续搜索
            if obj.__class__ not in _skip: # 如果不忽略
                result=_search(target,obj,recursions-1,search_str,verbose,cache,show_error)
                for path in result:
                    results.append(name+path)
        except Exception as err: # 忽略getattr()返回的AttributeError
            if not isinstance(err,AttributeError) and show_error:
                traceback.print_exc()

    if isinstance(start_obj,(list,tuple)): # 进一步搜索列表、元组项
        for i in range(len(start_obj)):
            name="[%d]"%i
            obj=start_obj[i]
            if target == obj:
                results.append(name)
            if obj.__class__ not in _skip:
                result=_search(target,obj,recursions-1,search_str,verbose,cache,show_error)
                for path in result:
                    results.append(name+path)

    if isinstance(start_obj,dict): # 进一步搜索字典项
        for key in start_obj.keys():
            if (search_str and target in key) or target == key:
                results.append("的字典键 "+repr(key))
            name="[%s]"%repr(key)
            obj=start_obj[key]
            if target == obj:
                results.append(name)
            if obj.__class__ not in _skip:
                result=_search(target,obj,recursions-1,search_str,verbose,cache,show_error)
                for path in result:
                    results.append(name+path)

    try:
        if cache is not None:
            cache[start_obj]=results
    except TypeError: # 某些类型如列表等无法作为字典键使用
        pass
    return results

def search(obj,start,recursions=3,search_str=True,\
           verbose=True,cache=True,show_error=True):
    """从一个起点开始搜索对象。
obj:待搜索的目标对象。
start:起点对象，也就是从哪里开始搜索。
recursions:最大递归层数，最小为1层。
search_str:是否搜索字符串的子串。
verbose:是否搜索以下划线开头的属性，如__init__等。
cache:是否启用缓存 (可加快搜索速度)，值为True,False,或者一个字典。
show_error:在getattr()内发生异常时，是否将异常输出至sys.stderr。
"""
    name=getattr(start,"__name__","obj") # 也可导入使用objectname函数
    if not isinstance(cache,dict):
        cache={} if cache else None
    results=_search(obj,start,recursions,search_str,\
                    verbose,cache,show_error)
    for i in range(len(results)):
        results[i]=name+results[i]
    return results

def test_make_list():
    #import pprint
    import pyobject
    lst=make_list(pyobject,3)
    lst_iter=list(make_iter(pyobject,3))
    #print(pprint.pformat(lst))
    print("make_list:",len(lst))
    print("make_iter:",len(lst_iter))

def test_search():
    import tkinter
    print(search(tkinter,sys,4))

def _format_size(size):  
    units = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]  
    base = 1024  
    i = 0  
    while size >= base and i < len(units) - 1:  # -1 因为有9个单位  
        size /= base  
        i += 1  
    return "{:.2f} {}".format(size,units[i])

def _iter_module(module,lst,called):
    recursions=1
    mem_used=0
    for attr in dir(module):
        obj=getattr(module,attr)
        if isinstance(obj,ModuleType):continue # 跳过其他的模块
        _make_list(obj,recursions,lst,called,all=True,show_error=False)
def _calc_module_memory(mod_name):
    module=sys.modules[mod_name]
    lst=[];called=[]
    _iter_module(module,lst,called)
    for obj in lst:
        mem_used+=sys.getsizeof(obj)
    return mem_used
def test_calc_module_memory():
    mod_name=input("输入要查询占用内存的模块名称：")
    if mod_name.strip():
        exec("import %s"%mod_name)
        mem_used=_calc_module_memory(mod_name)
        print("模块 %s 内存占用: %s" % (mod_name, _format_size(mem_used)))
def test_calc_total_memory():
    lst=[];called=[]
    for mod_name in sorted(list(sys.modules)):
        if mod_name=="sys":continue
        print("处理模块 %s" % mod_name, end="",flush=True)
        _iter_module(mod_name,lst,called)
        print(" 列表长度: %d" % (len(lst)),flush=True)
    total_mem=0
    for obj in lst:
        total_mem+=sys.getsizeof(obj)
    print("模块占用总内存: %s" % _format_size(total_mem))

if __name__=="__main__":
    test_make_list()
    test_search()
    #test_calc_module_memory()
    test_calc_total_memory()
