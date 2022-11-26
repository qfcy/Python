import sys,os,traceback
import uncompyle6.bin.uncompile as uncompiler
__version__='2.0.1'

def run_uncompile(filename):
    flag=False # 监测sys.stderr中有无警告或错误消息
    _w=sys.stderr.write
    def w(*arg,**kw):
        nonlocal flag
        flag=True
        _w(*arg,**kw)
    def start_check(): # 开始监测
        sys.stderr.write=w
    def end_check():  # 停止监测
        sys.stderr.write=_w

    tofilename=filename[:-1]
    if os.path.isfile(tofilename):
        result=input("文件%s已存在,要替换它吗? "%tofilename)
        if not result.lower().startswith('y'):return
    try:
        sys.stdout=open(tofilename,"w",encoding="utf-8")
        sys.argv[1]=filename
        start_check()
        uncompiler.main_bin()
    except Exception:
        end_check()
        print("文件%s反编译失败，错误消息详见%s"% (filename,tofilename)
              ,file=sys.stderr)
        #traceback.print_exc()
        traceback.print_exc(file=sys.stdout)
    else:
        end_check()
        if not flag:
            print("文件%s反编译成功"%filename,file=sys.stderr)
        else:
            print("文件%s反编译失败, 有警告或错误"%filename,file=sys.stderr)
            print("按Enter键继续...",end='',file=sys.stderr)
            input()
    finally:
        sys.stdout.close()

if __name__=="__main__":
    try:
        if len(sys.argv)>1:
            files=sys.argv[1:]
            sys.argv[0]=uncompiler.__file__
            sys.argv[1:]=['']
            for file in files:
                if not file.endswith(".pyc"):
                    print("警告: %s 可能不是pyc文件"%file,file=sys.stderr)
                run_uncompile(file)
        else:
            file=input("拖曳文件到本窗口,然后按回车:\n").strip('"')
            sys.argv[0]=uncompiler.__file__
            sys.argv.append('')
            run_uncompile(file)
    finally:
        sys.stdout=sys.__stdout__
