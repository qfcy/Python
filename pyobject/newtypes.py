import sys
from copy import deepcopy

NoneType=None.__class__
class newNoneType():
    """一种新的None类型。
与Python自带的NoneType类型相比,这种类型什么都能做,可以相加,相减,相乘,相除,被调用,等等,
, 即支持许多"魔法"方法; 但每个方法什么也不做,直接pass。
示例:
>>> none=newNoneType()
>>> none
>>> print(none)
newNoneType
>>> none.write()
>>> none.write=1
>>> none.write
1
>>> none+'1'
'1'
>>> none-1
-1
>>> none>0
False
>>> none>=0
True
>>> none<0
False
>>> none<=0
True
>>> none==None
True"""
    def __add__(self,other):
        return other
    def __bool__(self):
        return False
    def __call__(self,*args,**kwargs):
        return self
    def __eq__(self,other):
        availbles=self,newNoneType, None,NoneType, 0,''
        for availble in availbles:
            if other is availble:return True
        return False
    def __ge__(self,value):
        return value<=0
    def __getattr__(self,name):
        return self
    def __gt__(self,value):
        return value<0
    def __le__(self,value):
        return value>=0
    def __lt__(self,value):
        return value>0
    def __str__(self):
        return self.__class__.__name__
    def __repr__(self):
        return ''
    def __sub__(self,value):
        return -value
    def __neg__(self):
        return self
    def __setattr__(self,name,value):
        self.__dict__[name]=value
        return self

inf=1e315
class Infinity():
    """无穷大。
示例:
>>> inf=Infinity()
>>> inf
Infinity()
>>> print(inf)
∞
>>> print(-inf)
-∞
>>> float(inf)
inf
>>> inf==float(inf)
True
>>> -inf
-Infinity()
>>> inf>1e308
True
>>> inf<1e308
False
>>> inf>=1e308
True
>>> inf<=1e308
False
>>> -inf==-float(inf)
True
>>> -inf>0
False
>>> -inf<0
True
>>> -inf>=0
False
>>> -inf<=0
True
    """
    def __init__(self,neg=False):
        self.neg=neg
    def __eq__(self,value):
        return value is self or value==float(self)
    def __float__(self):
        return -inf if self.neg else inf
    def __ge__(self,value):
        # self>=value
        return not self.neg
    def __gt__(self,value):
        # self>value
        return not self<=value
    def __le__(self,value):
        # self<=value
        return (not self==value) if self.neg else (self==value)
    def __lt__(self,value):
        # self<value
        return self.neg
    def __neg__(self):
        return Infinity(neg=(not self.neg))
    def __str__(self):
        return ('-' if self.neg else '')+'∞'
    def __repr__(self):
        return "%sInfinity()"%('-' if self.neg else '')

##class StrangeList(list,tuple):
##    """一种可变的,奇怪的序列类型,同时继承内置list和tuple类。"""

class ObjDict:
    "对象字典"
    def __init__(self,obj):
        self.obj=obj
    def __getitem__(self,key):
        return getattr(self.obj,key)
    def __setitem__(self,key,value):
        setattr(self.obj,key,value)
    def __delitem__(self,key):
        delattr(self.obj,key)
    def get(self,key,default):
        return getattr(self.obj,key,default)

    def __iter__(self):
        return dir(self.obj).__iter__()
    def keys(self):
        return dir(self.obj)
    def clear(self):
        for key in self.keys():
            try:
                delattr(self.obj,key)
            except Exception as err:
                print(type(err).__name__+":", err,
                      file=sys.stderr)
    def __str__(self):
        return str(dict(self))

    def __copy__(self):
        return ObjDict(self.obj)
    def __deepcopy__(self,*args):
        newobj=deepcopy(self.obj)
        return ObjDict(newobj)
    def __repr__(self):
        try:
            return "ObjDict(%r)"%self.obj
        except AttributeError: # ObjDict对象没有obj属性时
            return object.__repr__(self)
    def todict(self):
        return dict(self)
    @staticmethod
    def dict_to_obj(dict):
        """>>> d=ObjDict(ObjDict(1)).todict()
>>> ObjDict.dict_to_obj(d)
ObjDict(1)
"""
        obj=object.__new__(dict["__class__"])
        obj.__dict__.update(dict)
        return obj
    # for pickle
    def __getstate__(self):
        return self.obj
    def __setstate__(self,arg):
        self.obj=arg

try:
    from pyobject.code_ import Code
except ImportError:pass
