from ctypes import *
import time

# 仅支持64位Python
malloc = windll.msvcrt.malloc
malloc.argtypes = [c_int64]
malloc.restype = c_int64
calloc = windll.msvcrt.calloc
calloc.argtypes = [c_int64]
calloc.restype = c_int64
free = windll.msvcrt.free
free.argtypes = [c_int64]
free.restype = c_int64

pointers = []
while True:
    pointer = malloc(2**28)
    print(hex(pointer))
    if pointer != 0:
        pointers.append(pointer)
    else:
        break
time.sleep(5)
for p in pointers:
    free(p)