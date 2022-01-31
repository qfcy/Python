import sys,os,traceback,marshal
import runpy

vars={"__annotations__":{},"__builtins__":__builtins__,"__doc__":None,
      "__loader__":__loader__,"__name__":"__main__","__package__":None,
      "__spec__":None,"sys":sys,"os":os}
_TITLE="PyShell"
__version__="1.3.2"

def exec_code(code):
    # 执行代码
    try:
        if code.strip():
            exec(compile(code,'<PyShell #{}>'.format(line),'single'),vars)
    except BaseException as err:
        handle(err)

def run_file(filename):
    code=open(filename,'rb').read()
    if filename.endswith(".pyc"):
        code=code[16:] if code[16]==227 else code[12:]
        code=marshal.loads(code)
    else:
        code=code.decode(encoding='utf-8').strip('\ufeff')
    backup=sys.argv
    sys.argv=sys.argv[1:]
    sys.path.append(os.path.split(filename)[0])
    vars["__file__"]=filename
    try:
        exec(code,vars)
    except:
        # 避免出现错误failed to execute script ...
        try:
            traceback.print_exc()
        except:pass
    sys.argv=backup

def in_pythonw():
    return "pythonw.exe" in sys.executable or "pyshellw.exe" in sys.executable

def handle(err):
    traceback.print_exc()

def ask_for_exit():
    msg="\n^C确实要退出吗?(Y/N) "
    print(msg,end='')
    try:
        if input().lower().startswith('y'):return 0
    except KeyboardInterrupt:
        return ask_for_exit(console)


def main():
    print("PyShell v%s"%__version__)
    # 执行autoexec.py
    try:
        autoexecfile=\
            (os.path.split(sys.argv[0])[0] or os.path.split(sys.executable)[0])\
                +"\\autoexec.py"
        run_file(autoexecfile)
    except BaseException as err:handle(err)

    # 处理命令行参数
    if len(sys.argv)>1:
        if sys.argv[1]=="-m":
            if len(sys.argv)==3:
                runpy.run_module(sys.argv[2],
                                 init_globals=vars)
            else:
                print("PyShell:\n用法:pyshell -m 模块名称\n运行一个模块。")
        else:
            filename=os.path.realpath(sys.argv[1])
            run_file(filename)
        return


    while True:
        try:
            if getattr(sys.stdin,"closed",True):
                return
            code=input(">>> ")

            exec_code(code)

        except KeyboardInterrupt:
            msg="\n^C确实要退出吗?(Y/N) "
            if ask_for_exit()==0:
                return
        except EOFError:break

if __name__=="__main__":main()
