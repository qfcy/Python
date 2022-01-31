import os
import importlib as __imp

def __import_mod(fmt_str="painter.%s"):
    path=os.path.split(__file__)[0]
    for i in range(20,0,-1):
        for j in range(9,-1,-1):
            for k in range(5,-1,-1):
                ver="v%i_%i"%(i,j)+('_%i'%k if k else '')
                #print("Trying to import %s"%ver)
                if not os.path.isfile("{}\{}.py".format(path,ver)):continue
                #exec("from painter.%s import Painter,main"%ver)
                module=__imp.__import__(fmt_str%ver)
                print("Painter %s"%ver)
                return getattr(module,ver,module)

try:
    mod=__import_mod()
    if not mod:raise ImportError("Could not find module painter.vx_x")
    scope=globals()
    #相当于from xxmodule import *
    for attr in dir(mod):
        scope[attr]=getattr(mod,attr,None)

    del mod,scope,attr
except ImportError:pass
