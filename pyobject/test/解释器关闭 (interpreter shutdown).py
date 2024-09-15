import sys,gc,pyobject
input=__builtins__.input
exec=__builtins__.exec
compile=__builtins__.compile
dict_=globals()
print('Allocated blocks',sys.getallocatedblocks())

def debug(dict_):
    while 1:
        s=input('>>> ').rstrip()
        if s:
            if s=='continue':break
            try:exec(compile(s,'<shell>','single'),dict_)
            except Exception as err:
                print(type(err).__name__+':'+str(err))


ignore = ['__main__','io','sys',
          'importlib._bootstrap','importlib._bootstrap_external',
          'importlib']

l = list(sys.modules.values())
for mod in reversed(l):
    if hasattr(mod,'__file__') and getattr(mod,'__name__','') not in ignore:
        print('cleaning',getattr(mod,'__name__','<unknown>'))
        vars(mod).clear()

gc.collect()
print('Allocated blocks',sys.getallocatedblocks())
debug(dict_)
