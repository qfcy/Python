from distutils.core import setup
from Cython.Build import cythonize
import sys,os,traceback

filename = sys.argv[1] if len(sys.argv)==2 \
           else input("拖曳或输入文件名: ")
sys.argv[1:] = ['build_ext','--inplace']
try:
    setup(
        name = os.path.splitext(os.path.split(filename)[1])[0],
        ext_modules = cythonize(filename),
    )
except (Exception,SystemExit):
    traceback.print_exc()
os.system('pause')