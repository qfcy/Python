import sys,os,traceback
import uncompyle6.bin.uncompile as uncompiler
__version__='2.0.1'

def run_uncompile(filename):
    # 截获sys.stderr中的警告和错误消息
    message=""
    _write=sys.stderr.write
    def write(text,*arg,**kw):
        nonlocal message
        message+=text # 截获消息
        #_write(text,*arg,**kw)
    def start_capture(): # 开始监测,修改sys.stderr.write方法
        sys.stderr.write=write
    def end_capture():  # 停止监测
        sys.stderr.write=_write

    tofilename=filename[:-1]
    if os.path.isfile(tofilename):
        result=input("文件%s已存在,要替换它吗? (Y/N)"%tofilename)
        if not result.lower().startswith('y'):return
    try:
        sys.stdout=open(tofilename,"w",encoding="utf-8") # 替换sys.stdout
        sys.argv[1]=filename
        start_capture()
        uncompiler.main_bin() # 运行uncompile
    except KeyboardInterrupt:
        end_capture();print("用户中断了反编译",file=sys.stderr)
        sys.stdout.close();return
    except SystemExit as err:
        end_capture()
        print("退出状态码:",err.code,file=sys.stderr)
    except BaseException:
        end_capture()
        print("文件%s反编译失败，错误消息详见%s"% (filename,tofilename)
              ,file=sys.stderr)
        traceback.print_exc(file=sys.stdout)
        print("按Enter键继续...",end='',file=sys.stderr)
        input()
        sys.stdout.close();return
    else:
        end_capture()
    if not message:
        print("文件%s反编译成功"%filename,file=sys.stderr)
    else:
        print("文件%s反编译可能失败，警告/错误消息详见%s" % (
              filename,tofilename), file=sys.stderr)
        sys.stdout.write(message)
    print("按Enter键继续...",end='',file=sys.stderr)
    input()
    sys.stdout.close()

if __name__=="__main__":
    try:
        if len(sys.argv)>1:
            files=sys.argv[1:]
            sys.argv[0]=uncompiler.__file__
            sys.argv[1:]=['']
            for file in files:
                if not file.lower().endswith(".pyc"):
                    print("警告: %s 可能不是pyc文件"%file,file=sys.stderr)
                run_uncompile(file)
        else:
            file=input("拖曳文件到本窗口,然后按回车:\n").strip('"')
            sys.argv[0]=uncompiler.__file__
            sys.argv.append('')
            run_uncompile(file)
    finally:
        sys.stdout=sys.__stdout__
