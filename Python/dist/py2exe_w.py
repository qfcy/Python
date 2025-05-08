# 用py2exe打包exe的脚本（无黑色console窗口)
from traceback import print_exc as p
import sys,os
try:
    from distutils.core import setup
    import py2exe
    #os.chdir('d:\\it\\python')

    if len(sys.argv) > 1:
        args=sys.argv[1:]
        sys.argv[1]='py2exe'
        del sys.argv[2:]
        for file in args:
            print('File:',file)
            icon=input('图标:')
            try:setup(windows=[{'script':file,
                                'icon_resources': [(1,os.path.realpath(icon))] if icon else []}])
            except:p()
except:
    p()
os.system('pause')
