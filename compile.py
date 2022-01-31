"compile.py - 用于编译python文件的脚本"
import sys,os,shutil
currdir = os.path.split(__file__)[0]
if len(sys.argv) > 1:
    import py_compile
    for filename in sys.argv[1:]:
        if os.path.isfile(filename):
            pycfile = py_compile.compile(filename)#,optimize=2)
            print('已编译文件 ' + filename)
            if os.path.isfile(pycfile):
                shutil.copy(pycfile, os.path.splitext(filename)[0]+".pyc" )
                print('复制 {} 到 {}'.format(pycfile,
                                os.path.splitext(filename)[0]+".pyc"))

else:
    print("欢迎使用",__doc__,end='\n\n')
    result = input('是否编译当前目录 (%s) 下的所有文件?' % currdir)
    if result.lower().startswith('y'):
        import compileall
        compileall.compile_dir(currdir, maxlevels=1, optimize=1)
