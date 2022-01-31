import sys
from pyobject.search import make_iter

def printer(*args):
    try:
        print(*args)
    except KeyboardInterrupt:
        printer(*args)

size=0
l=[]
iter=make_iter(sys.modules,4)
for obj in iter:
    try:
        if obj not in l:
            size+=sys.getsizeof(obj)
            l.append(obj)
    except KeyboardInterrupt:
        printer(size)

print(size)
