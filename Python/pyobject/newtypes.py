import sys
from copy import deepcopy
from math import inf

NoneType=None.__class__
class NewNoneType():
    """A new None type designed to replace any objects with practical functionality.
Compared to Python's built-in NoneType, this type can do anything.
It can be added, subtracted, multiplied, called, etc, \
supporting many "magic" methods and interfaces.
However, these methods do nothing and only return a default value.
Examples (partial usage):
>>> none=NewNoneType()
>>> none
>>> print(none)
NewNoneType
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
        availbles=(self, NewNoneType, None, NoneType, 0, '')
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

class Infinity():
    """A fake infinity type.
Examples:
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

class ObjDict:
    "A fake dictionary based on an object's attibutes."
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

class Copier:
    "Copy other objects' attributes and mimic their behavior."
    def __init__(self,obj,copy_internal=False,onerror=None):
        """obj: The object to be copied.
copy_internal: Whether to copy magic methods.
onerror: A callback function accepting an exception object \
that will be called when any errors occur."""
        self._source_obj=obj
        for attr in dir(obj):
            if copy_internal or not (attr.startswith("__") 
                    and attr.endswith("__")):
                try:
                    setattr(self,attr,getattr(obj,attr))
                except Exception as err:
                    if onerror is not None:onerror(err)

if __name__=="__main__":
    import doctest
    doctest.testmod() # Ignore failure messages indicating "expected nothing but got <BLANKLINE>"