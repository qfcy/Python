"搜索python对象的模块"
import traceback
from types import WrapperDescriptorType,MethodWrapperType,\
     MethodDescriptorType,ClassMethodDescriptorType

__all__=["make_list","make_iter","search"]
_skip=(WrapperDescriptorType, MethodWrapperType,\
     MethodDescriptorType, ClassMethodDescriptorType) #自动忽略这些类型, 加快速度

def _make_list(start_obj,level,recursions,_list,all=False):
    if level>=recursions:return

    for attr in dir(start_obj):
        if all or not attr.startswith("__"):
            try:
                obj=getattr(start_obj,attr)
                if obj not in _list:_list.append(obj)
                if obj.__class__ not in _skip:
                    _make_list(obj,level+1,recursions,_list,all)
            except Exception:
                traceback.print_exc()
    if isinstance(start_obj,list):
        for item in start_obj:
            if item not in _list:_list.append(item)
            if obj.__class__ not in _skip:
                _make_list(item,level+1,recursions,_list,all)
    if isinstance(start_obj,dict):
        for obj in start_obj.keys():
            if obj not in _list:_list.append(obj)
        for obj in start_obj.values():
            if obj not in _list:_list.append(obj)
            if obj.__class__ not in _skip:
                _make_list(obj,level+1,recursions,_list,all)

def make_list(start_obj,recursions=2,all=False):
    """创建一个包含大量对象的列表。
start:开始搜索的对象
recursion:递归次数
all:是否将对象的特殊属性(如__init__)加入列表"""
    list=[]
    _make_list(start_obj,0,recursions,list,all)
    return list

def make_iter(start_obj,recursions,all=False,level=0):
    """创建一个对象的迭代器, 功能、参数与make_list相同, 
make_iter创建的迭代器可能会返回重复的对象, 而make_list不会。
"""
    if level>=recursions:return

    for attr in dir(start_obj):
        if all or not attr.startswith("__"):
            try:
                obj=getattr(start_obj,attr)
                yield obj
                # 跳过method_wrapper类型
                # 经测试, 使用obj.__class__比使用type(obj)更快
                if obj.__class__ not in _skip:
                    for obj in make_iter(obj,recursions,all,level+1):
                        yield obj
            except Exception:
                traceback.print_exc()
    if isinstance(start_obj,list):
        for item in start_obj:
            try:
                yield item
                if item.__class__ not in _skip:
                    for obj in make_iter(obj,recursions,all,level+1):
                        yield obj
            except Exception:traceback.print_exc()
    if isinstance(start_obj,dict):
        for obj in start_obj.keys():
            yield obj
        for obj in start_obj.values():
            try:
                yield obj
                if obj.__class__ not in _skip:
                    for obj in make_iter(obj,recursions,all,level+1):
                        yield obj
            except Exception:traceback.print_exc()

def _search(obj,start_obj,level,_results,recursions=3,name="obj",search_str=False):

    if level>=recursions:return
    search_str=search_str and isinstance(obj,str)

    for attrname in dir(start_obj):
        try:
            _name="{}.{}".format(name,attrname)
            if search_str and obj in attrname:
                _results.append(_name)
            obj2=getattr(start_obj,attrname)
            if obj == obj2:
                _results.append(_name)
            if obj2.__class__ not in _skip:
                _search(obj,obj2,level+1,_results,recursions,_name)
        except Exception:
            #traceback.print_exc()
            pass

    if isinstance(start_obj,list):
        for i in range(len(start_obj)):
            _name="{}[{}]".format(name,i)
            if obj == start_obj[i]:
                _results.append(_name)
            if start_obj.__class__ not in _skip:
                _search(obj,obj2,level+1,_results,recursions,_name)

    if isinstance(start_obj,dict):
        for key in start_obj.keys():
            if (search_str and obj in key) or obj == key:
                _results.append("字典 {} 的键 {}".format(name,key))
            obj2=start_obj[key]
            _name="{}[{}]".format(name,key)
            if obj == obj2:
                _results.append(_name)
            if start_obj.__class__ not in _skip:
                _search(obj,obj2,level+1,_results,recursions,_name)


def search(obj,start,recursions=3,search_str=True):
    """从一个起点开始搜索对象
obj:待搜索的对象
start:起点对象
recursion:递归次数
search_str:是否搜索字符串
"""

    results=[]
    _search(obj,start,0,results,recursions,
                name=getattr(start,"__name__","obj"),search_str=search_str)
    return results

def test_make_list():
    import pprint
    import pyobject
    print(pprint.pformat(make_list(pyobject)))

def test_search():
    import pyobject
    print(search('exc',traceback,3,search_str=True))

if __name__=="__main__":
    #test_make_list()
    test_search()
