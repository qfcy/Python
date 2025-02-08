"提供操作Python字节码的工具。Provides tools for manipulating Python native bytecode."
import sys
try:
    from importlib._bootstrap_external import MAGIC_NUMBER
except ImportError:
    from importlib._bootstrap import MAGIC_NUMBER
from types import CodeType, FunctionType
from collections import OrderedDict
import marshal,io,builtins
import dis
import pickle
import traceback
from pyobject import desc

__all__ = ["Code"]

_default_code=compile('','','exec')
_is_py38=hasattr(_default_code, 'co_posonlyargcount') # 是否为3.8及以上版本
_is_py310=hasattr(_default_code, 'co_linetable') # 是否为3.10及以上版本
_is_py311=hasattr(_default_code, 'co_exceptiontable') # 是否为3.11及以上版本
class Code:
    """
# Example usage, also for doctest
>>> def f():print("Hello")

>>> c=Code.fromfunc(f)
>>> c.co_consts
(None, 'Hello')
>>> c.co_consts=(None, 'Hello World!')
>>> c.exec()
Hello World!
>>> 
>>> import os,pickle
>>> temp=os.getenv('temp')
>>> with open(os.path.join(temp,"temp.pkl"),'wb') as f:
...     pickle.dump(c,f)
... 
>>> 
>>> f=open(os.path.join(temp,"temp.pkl"),'rb')
>>> pickle.load(f).to_func()()
Hello World!
>>> 
>>> c.to_pycfile(os.path.join(temp,"temppyc.pyc"))
>>> sys.path.append(temp)
>>> import temppyc
Hello World!
>>> Code.from_pycfile(os.path.join(temp,"temppyc.pyc")).exec()
Hello World!
"""
# 关于CodeType: 
# 初始化参数：
# code(argcount, kwonlyargcount, nlocals, stacksize, flags, codestring,
#    constants, names, varnames, filename, name, firstlineno,
#    lnotab[, freevars[, cellvars]])
# 初始化参数 (Python 3.11+)：
# code(argcount, posonlyargcount, kwonlyargcount, nlocals, stacksize, flags, codestring, 
# constants, names, varnames, filename, name, qualname, firstlineno, linetable, 
# exceptiontable, freevars=(), cellvars=(), /)
# Python 3.10中没有qualname和exceptiontable这两个参数
# Python 3.8增加了属性co_posonlyargcount，而Python 3.11的字节码有较大的改动

    if _is_py310: # Python 3.10及以上版本
        _default_args=OrderedDict(
             [('co_argcount',0),
              ('co_posonlyargcount',0),
              ('co_kwonlyargcount',0),
              ('co_nlocals',0),
              ('co_stacksize',1),
              # 如果是函数中, 则为OPTIMIZED, NEWLOCALS, NOFREE; Python 3.11及以上为OPTIMIZED, NEWLOCALS
              ('co_flags',0), # 无flag
              ('co_code',_default_code.co_code),# 具体因Python版本而异
              ('co_consts',(None,)),
              ('co_names',()),
              ('co_varnames',()),
              ('co_filename',''),
              ('co_name',''),
              ('co_qualname',''), # 3.11+
              ('co_firstlineno',1),
              ('co_linetable',b''),
              ('co_exceptiontable',b''), # 3.11+
              ('co_freevars',()),
              ('co_cellvars',())
              ])
        if not _is_py311: # Python 3.10
            _default_args["co_flags"]=64 # NOFREE
            del _default_args['co_qualname']
            del _default_args['co_exceptiontable']
    else:
        # 按顺序的字典
        _default_args=OrderedDict(
             [('co_argcount',0),
              ('co_kwonlyargcount',0),
              ('co_nlocals',0),
              ('co_stacksize',1),
              # 如果是函数中, 则为OPTIMIZED, NEWLOCALS, NOFREE
              ('co_flags',64), # NOFREE
              ('co_code',b'd\x00S\x00'),# LOAD_CONST    0 (None)
                                        # RETURN_VALUE
              ('co_consts',(None,)),
              ('co_names',()),
              ('co_varnames',()),
              ('co_filename',''),
              ('co_name',''),
              ('co_firstlineno',1),
              ('co_lnotab',b''),
              ('co_freevars',()),
              ('co_cellvars',())
              ])
        # 3.8~3.9
        if _is_py38:
            _default_args['co_posonlyargcount']=0
            _default_args.move_to_end('co_posonlyargcount', last=False)
            _default_args.move_to_end('co_argcount', last=False)

    _arg_types={key:type(value) for key,value in _default_args.items()}
    def __init__(self,code=None):
        """Initialize the code object. \
The code argument can be either Code or the built-in CodeType."""
        super().__setattr__('_args',self._default_args.copy())
        if code is not None:
            if isinstance(code,Code):
                self._args = code._args.copy()
                self._update_code()
            else:
                self._code=code
                for key in self._args.keys():
                    self._args[key]=getattr(code,key)
        else:
            self._update_code()
    
    def _update_code(self):
        self._code=CodeType(*self._args.values())
    def exec(self,globals_=None,locals_=None):
        "Execute the code using globals_ and locals_ scopes."
        default={"__builtins__":__builtins__,"__doc__":None,
                  "__loader__":__loader__,"__name__":"__main__"}
        globals_ = globals_ or default
        if not locals_:locals_ = default.copy()
        return exec(self._code,globals_,locals_)
    def eval(self,globals_=None,locals_=None):
        "Evaluate the code using globals_ and locals_ scopes."
        default={"__builtins__":__builtins__,"__doc__":None,
                  "__loader__":__loader__,"__name__":"__main__"}
        globals_ = globals_ or default
        if not locals_:locals_ = default.copy()
        return eval(self._code,globals_,locals_)
    def __getattr__(self,name):
        _args=object.__getattribute__(self,'_args')
        if name in _args:
            return _args[name]
        else:
            if hasattr(self._code,name) and not name.startswith("__"):
                return getattr(self._code,name) # self._code的其他属性
            else:
                # 调用super()耗时较大, 因此改用object
                return object.__getattribute__(self,name)
    def __setattr__(self,name,value):
        if name not in self._args:
            return object.__setattr__(self,name,value)
        if not isinstance(value,self._arg_types[name]):
            raise TypeError("Illegal attribute %s" % name)
        self._args[name]=value
        self._update_code()
    def __dir__(self):
        extra=[attr for attr in dir(self._code) \
            if attr not in self._args and not attr.startswith("__")] # self._code的其他属性
        return object.__dir__(self) + list(self._args.keys()) + extra
    # 用于pickle模块保存状态
    def __getstate__(self):
        return self._args
    def __setstate__(self,state):
        super().__setattr__('_args',self._default_args.copy())
        for key in state: # 删除来自新版中不兼容的项
            if key not in self._args:
                del state[key]
        self._args.update(state)
        self._update_code()
    @classmethod
    def fromfunc(cls,function):
        "Create a Code instance from a function object."
        c=function.__code__
        return cls(c)
    @classmethod
    def fromstring(cls,string,mode='exec',filename=''):
        "Create a Code instance from a source code string using compile()."
        return cls(compile(string,filename,mode))
    def to_code(self):
        "Convert the code object to a built-in CodeType."
        return self._code
    def to_func(self,globals_=None,name=''):
        "Convert the code object to a function."
        if globals_ is None:
            # 默认的全局命名空间包含内置函数
            globals_={"__builtins__":builtins}
        return FunctionType(self._code,globals_,name)
    def to_pycfile(self,filename):
        "Dump the code object into a .pyc file using marshal."
        with open(filename,'wb') as f:
            f.write(MAGIC_NUMBER)
            if sys.version_info.minor>=7:
                f.write(b'\x00'*12)
            else:
                f.write(b'\x00'*8)
            marshal.dump(self._code,f)
    @classmethod
    def from_pycfile(cls,filename):
        "Create a Code instance from a .pyc file using marshal."
        with open(filename,'rb') as f:
            data=f.read()
            header_len = 16 if data[16] in (0x63,0xe3) else 12 # 0xe3为cpython，0x63为pypy
            data=data[header_len:]
            return cls(marshal.loads(data))
    @classmethod
    def from_file(cls,filename):
        "Create a Code instance from a .pyc or .py file."
        if filename.lower().endswith('.pyc'):
            return Code.from_pycfile(filename)
        else: # .py或pyw文件 (默认utf-8编码)
            with open(filename,'rb') as f:
                data=f.read().decode('utf-8')
            return Code(compile(data,filename,'exec'))
    def pickle(self,filename):
        "Dump the code object into pickle format."
        with open(filename,'wb') as f:
            pickle.dump(self,f)
    def show(self,*args,**kw):
        "Display the attributes of the code object, including co_code, co_consts, etc."
        desc(self._code,*args,**kw)
    def info(self):
        "Display the basic information about the bytecode."
        dis.show_code(self._code)
    def dis(self,*args,**kw):
        "Display the disassembly of the bytecode using dis.dis()."
        dis.dis(self._code,*args,**kw)
    def decompile(self,version=None,*args,**kw):
        "Decompile the code object to source code using uncompyle6 library."
        try:
            from uncompyle6.main import decompile
        except ImportError as err:
            raise NotImplementedError(
                    "Missing uncompyle6 library (%s: %s)" % (
                    type(err).__name__,str(err)))
        out=io.StringIO()
        if version:
            decompile(self._code,version,out,*args,**kw)
        else:
            decompile(self._code,out=out,**kw)
        out.seek(0)
        return out.read()

def interactive(mode='exec'):
    while 1:
        str=input('>> ')
        if not str.strip():
            print('Please input a code string!')
        else:
            try:
                code=Code.fromstring(str,mode=mode)
                code.dis()
            except Exception:
                traceback.print_exc()


if __name__=="__main__":
    import doctest
    doctest.testmod()
    if len(sys.argv)>1:
            ps='>>> '
            statement='c=Code.from_file(%s)'%repr(sys.argv[1].strip('"'))
            print(ps + statement)
            try:exec(statement)
            except Exception:traceback.print_exc()
            while True:
                try:
                    code=input(ps)
                    if code.strip():
                        exec(compile(code,'<interactive>','single'))
                except (Exception,KeyboardInterrupt):
                    traceback.print_exc()
    else:
        interactive()
