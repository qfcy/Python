# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.2rc1 (tags/v3.7.2rc1:75a402a217, Dec 11 2018, 22:09:03) [MSC v.1916 32 bit (Intel)]
# Embedded file name: ulang\runtime\env.py
import ast, dis, imp, math, os, sys, getopt, time, threading, trace
from datetime import datetime
from ulang.parser.core import Parser

def parse_and_compile(input_file):
    with open(input_file, 'r') as (file):
        parser = Parser()
        nodes = parser.parse(source=(file.read()),
          filename=input_file)
        return compile(nodes, input_file, 'exec')


def load_ulang_module(name, globals, fromlist=(), level=0):
    path = name.replace('.', '/') + '.ul'
    if sys.platform == 'win32':
        path = path.replace('/', '\\')
    code = parse_and_compile(path)
    if code is None:
        raise ModuleNotFoundError(name)
    modules = []
    tail = name

    # Avoid dead code: name
    def _modname(name):
        if modules:
            return modules[(-1)].__name__ + '.' + name
        else:
            return name
    module_name = _modname
    
    index = 0
    while index != -1:
        index = tail.find('.')
        head, tail = tail[:index], tail[index + 1:]
        if index == -1:
            head = tail
            module = imp.new_module(module_name(tail))
            globals_ = create_globals(argv=(globals['ARGV']))
            module.__dict__.update(globals_)
            module.__dict__['__file__'] = os.path.abspath(path)
            exec(code, module.__dict__)
        else:
            module = imp.new_module(module_name(head))
        if modules:
            modules[(-1)].__dict__[head] = module
        modules.append(module)

    result = modules[0]
    if len(modules) > 1:
        if fromlist is not None:
            for sym in fromlist:
                if sym == '*':
                    for k in module.__dict__:
                        if k not in globals:
                            result.__dict__[k] = module.__dict__[k]

                    break
                else:
                    result.__dict__[sym] = module.__dict__[sym]

    return result


class Thread(threading.Thread):
    __doc__ = '\n    A traced thread wrapper.\n    '

    def __init__(self, *args, **kw):
        (threading.Thread.__init__)(self, *args, **kw)
        self.killed = False

    def start(self):
        self._Thread__run_backup = self.run
        self.run = self._Thread__run
        threading.Thread.start(self)

    def __run(self):
        sys.settrace(self.globaltrace)
        self._Thread__run_backup()
        self.run = self._Thread__run_backup

    def globaltrace(self, frame, event, arg):
        if event == 'call':
            return self.localtrace
        return

    def localtrace(self, frame, event, arg):
        if self.killed:
            if event == 'line':
                raise SystemExit
        return self.localtrace

    def kill(self):
        self.killed = True


def fix_builtins(builtins):
    from inspect import isclass
    for k, v in __builtins__.items():
        if isclass(v) and issubclass(v, BaseException):
            builtins[k] = v

    return builtins


def __builtin_div(a, b):
    if isinstance(a, int):
        if isinstance(b, int):
            return math.floor(a / b)
    return a / b


def __builtin_rem(a, b):
    if isinstance(a, int):
        if isinstance(b, int):
            return int(a % b)
    return a % b


def create_globals(argv=[], fname=''):
    """
    Create the global runtime enviroment for the µlang program.
    """

    def local_str(x):

        def container_to_str(c, start='', end='', ptr=None):
            _str = start
            for i, item in enumerate(c):
                if i:
                    _str += ', '
                if ptr is None:
                    _str += local_str(item)
                else:
                    _str += ptr(c, item)

            _str += end
            return _str

        if x is None:
            return 'nil'
        if isinstance(x, bool):
            if x:
                return 'true'
            return 'false'
        if isinstance(x, list):
            return container_to_str(x, '[', ']')
        if isinstance(x, tuple):
            return container_to_str(x)
        if isinstance(x, dict):
            return container_to_str(x, '{', '}', lambda c, k: '%s: %s' % (k, c[k]))
        if isinstance(x, set):
            return container_to_str(x, '{', '}')
        return str(x)

    def local_print(*objs, sep=' ', end='', file=sys.stdout, flush=False):
        """Prints thy values to a stream, or to stdout by default."""
        for obj in objs:
            file.write(local_str(obj))
            if obj != objs[(-1)]:
                file.write(sep)

        file.write(end)
        if flush:
            file.flush()

    def local_import(name, globals=None, locals=None, fromlist=(), level=0):
        """Import a ulang module, if no ulang module is found, 
        import the python modules.
        """
        try:
            return load_ulang_module(name, globals, fromlist, level)
        except:
            return __import__(name, globals, locals, fromlist, level)

    def local_assert(expr, msg=None):
        assert expr, msg

    def builtin_spawn(target, *args):
        """ Spawn and start a new concurrency task. """
        th = Thread(target=target, args=args, daemon=True)
        th.start()
        return th

    def builtin_kill(th):
        """ Kill a given task if it is running. """
        if isinstance(th, Thread):
            if th == threading.currentThread():
                sys.exit()
            else:
                if th.isAlive():
                    th.kill()

    def builtin_self():
        """ Return the task id of current task. """
        return threading.currentThread()

    def pip_install(*packages, cmd='install'):
        """ Trigger a pip command. """
        import pip._internal
        return pip._internal.main([cmd, *packages])

    def eval_print(expr):
        if expr is None:
            return
        try:
            expr()
        except Exception:
            local_print(expr, end='\n')

    cwd = os.getcwd()
    if cwd not in sys.path:
        sys.path.append(cwd)
    return {'print':local_print, 
     'println':lambda *objs: local_print(*objs, **{'end': '\n'}), 
     'assert':local_assert, 
     'len':len, 
     'enumerate':enumerate, 
     'all':all, 
     'any':any, 
     'range':range, 
     'round':round, 
     'input':input, 
     'reverse':reversed, 
     'super':super, 
     'locals':lambda : locals(), 
     'bool':bool, 
     'float':float, 
     'int':int, 
     'str':str, 
     'list':list, 
     'dict':dict, 
     'set':set, 
     'tuple':lambda *args: args, 
     'char':chr, 
     'ord':ord, 
     'bytes':lambda s, encoding='ascii': bytes(s, encoding), 
     'typeof':lambda x: x.__class__.__name__, 
     'isa':lambda x, t: isinstance(x, t), 
     'max':max, 
     'min':min, 
     'map':map, 
     'filter':filter, 
     'zip':zip, 
     'staticmethod':staticmethod, 
     'property':property, 
     'ceil':math.ceil, 
     'floor':math.floor, 
     'fabs':math.fabs, 
     'sqrt':math.sqrt, 
     'log':math.log, 
     'log10':math.log10, 
     'exp':math.exp, 
     'pow':math.pow, 
     'sin':math.sin, 
     'cos':math.cos, 
     'tan':math.tan, 
     'asin':math.asin, 
     'acos':math.acos, 
     'atan':math.atan, 
     'spawn':builtin_spawn, 
     'kill':builtin_kill, 
     'self':builtin_self, 
     'quit':sys.exit, 
     'open':open, 
     'install':pip_install, 
     'time':time.time, 
     'year':lambda : datetime.now().year, 
     'month':lambda : datetime.now().month, 
     'day':lambda : datetime.now().day, 
     'hour':lambda : datetime.now().hour, 
     'minute':lambda : datetime.now().minute, 
     'second':lambda : datetime.now().second, 
     'microsecond':lambda : datetime.now().microsecond, 
     'sleep':time.sleep, 
     'delay':lambda ms: time.sleep(ms / 1000), 
     'delayMicroseconds':lambda us: time.sleep(us / 1000000), 
     'PI':math.pi, 
     'ARGV':argv, 
     '__builtins__':fix_builtins({'__import__':local_import, 
      '__build_class__':__build_class__, 
      '__name__':'__main__', 
      '__file__':fname, 
      '__print__':eval_print, 
      '___':None, 
      '__div__':__builtin_div, 
      '__rem__':__builtin_rem})
      }
# okay decompiling E:\ulang\ulang-0.2.2.exe_extracted\PYZ-00.pyz_extracted\ulang.runtime.env.pyc
