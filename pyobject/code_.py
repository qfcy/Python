"提供操作Python字节码的工具。"
import sys
try:
    from importlib._bootstrap_external import MAGIC_NUMBER
except ImportError:
    from importlib._bootstrap import MAGIC_NUMBER
from types import CodeType, FunctionType
from collections import OrderedDict
import marshal
import dis
import pickle
import traceback
from pyobject import desc

_py38=hasattr(compile('','','exec'), 'co_posonlyargcount')
class Code:
    """
# 用于doctest
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
# 参数
# code(argcount, kwonlyargcount, nlocals, stacksize, flags, codestring,
#    constants, names, varnames, filename, name, firstlineno,
#    lnotab[, freevars[, cellvars]])
# 属性:
#co_argcount
#co_cellvars
#co_code
#co_consts
#co_filename
#co_firstlineno
#co_flags
#co_freevars
#co_kwonlyargcount
#co_lnotab
#co_name
#co_names
#co_nlocals
#co_stacksize
#co_varnames
# 在Python 3.8中, 增加了属性co_posonlyargcount

    # 按顺序
    _default_args=OrderedDict(
         [('co_argcount',0),
          ('co_kwonlyargcount',0),
          ('co_nlocals',0),
          ('co_stacksize',1),
          # 如果是函数中的code, 则是OPTIMIZED, NEWLOCALS, NOFREE
          ('co_flags',64), # NOFREE
          ('co_code',b'd\x00S\x00'),#1   LOAD_CONST    0 (None)
                                    #2   RETURN_VALUE
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
    # 与Python3.8及以上版本兼容
    if _py38:
        _default_args['co_posonlyargcount']=0
        _default_args.move_to_end('co_posonlyargcount', last=False)
        _default_args.move_to_end('co_argcount', last=False)

    _arg_types={key:type(value) for key,value in _default_args.items()}
    def __init__(self,code=None,auto_update=True):
        super().__setattr__('_args',self._default_args.copy())
        if code is not None:
            if isinstance(code,Code):
                self._args = code._args
                self._update_code()
            else:
                self._code=code
                for key in self._args.keys():
                    self._args[key]=getattr(code,key)
        else:
            self._update_code()
        self.auto_update=auto_update
    def __getattr__(self,name):
        _args=object.__getattribute__(self,'_args')
        if name in _args:
            return _args[name]
        else:
            # 调用super()耗时较大, 所以改用object
            return object.__getattribute__(self,name)
    def __setattr__(self,name,value):
        if name not in self._args:
            return object.__setattr__(self,name,value)
        if not isinstance(value,self._arg_types[name]):
            raise TypeError(name,value)
        self._args[name]=value
        if self.auto_update: self._update_code()
    def _update_code(self):
        self._code=CodeType(*self._args.values())
    def exec(self,globals_=None,locals_=None):
        if not self.auto_update: self._update_code()

        default={"__builtins__":__builtins__,"__doc__":None,
                  "__loader__":__loader__,"__name__":"__main__"}
        globals_ = globals_ or default
        if not locals_:locals_ = default.copy()
        return exec(self._code,globals_,locals_)
    def eval(self,globals_=None,locals_=None):
        if not self.auto_update: self._update_code()
        return eval(self._code,globals_,locals_)

    # for pickle
    def __getstate__(self):
        return self._args
    def __setstate__(self,state):
        super().__setattr__('_args',self._default_args.copy())
        self._args.update(state)
        if not _py38 and 'co_posonlyargcount' in state:
            del state['co_posonlyargcount']
        self._update_code()
    def __dir__(self):
        return object.__dir__(self) + list(self._args.keys())
    @classmethod
    def fromfunc(cls,function):
        c=function.__code__
        return cls(c)
    @classmethod
    def fromstring(cls,string,mode='exec',filename=''):
        return cls(compile(string,filename,mode))
    def to_code(self):
        return self._code
    def to_func(self,globals_=None,name=''):
        if globals_ is None:
            # 默认
            import builtins
            globals_=vars(builtins)
        return FunctionType(self._code,globals_,name)
    def to_pycfile(self,filename):
        with open(filename,'wb') as f:
            f.write(MAGIC_NUMBER)
            if sys.winver>='3.7':
                f.write(b'\x00'*12)
            else:
                f.write(b'\x00'*8)
            marshal.dump(self._code,f)
    @classmethod
    def from_pycfile(cls,filename):
        with open(filename,'rb') as f:
            data=f.read()
            header = 16 if data[16]==227 else 12
            data=data[header:]
            return cls(marshal.loads(data))
    @classmethod
    def from_file(cls,filename):
        if filename.lower().endswith('.pyc'):
            return Code.from_pycfile(filename)
        else: # .py或pyw文件 (默认utf-8编码)
            with open(filename,'rb') as f:
                data=f.read().decode('utf-8')
            return Code(compile(data,filename,'exec'))
    def pickle(self,filename):
        with open(filename,'wb') as f:
            pickle.dump(self,f)
    def show(self,*args,**kw):
        desc(self._code,*args,**kw)
    view=show
    def info(self):
        dis.show_code(self._code)
    def dis(self,*args,**kw):
        dis.dis(self._code,*args,**kw)

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
