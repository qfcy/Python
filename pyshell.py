# coding:utf-8
import sys,os,traceback,marshal,builtins
import runpy

vars={"__annotations__":{},"__builtins__":__builtins__,"__doc__":None,
      "__loader__":__loader__,"__name__":"__main__","__package__":None,
      "__spec__":None,"sys":sys,"os":os}
_TITLE="PyShell"
__version__="1.3.2"

def exec_code(code,line=0):
    # 执行代码
    try:
##        result=eval(code,vars)
##        builtins._ = result
##        if result is not None:print(repr(result))
##    except SyntaxError:
##        try:
##            exec(code,vars)
##        except BaseException as err:
##            try:raise err from None
##            except:handle(err)
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
    exec(code,vars)
    sys.argv=backup

def in_pythonw():
    return "pythonw.exe" in sys.executable or "pyshellw.exe" in sys.executable

def handle(err):
    traceback.print_exc()

def ask_for_exit(console=None):
    msg="\n^C确实要退出吗?(Y/N) "
    if console:console.ctext(msg,"green",None,"bold",end='')
    else:print(msg,end='')
    try:
        if input().lower().startswith('y'):return 0
    except KeyboardInterrupt:
        return ask_for_exit(console)


def main():
    # 执行autoexec.py
    try:
        autoexecfile=os.path.split(sys.argv[0])[0]+"\\autoexec.py"
        run_file(autoexecfile)
    except BaseException as err:handle(err)

    # 处理命令行参数
    if len(sys.argv)>1:
        if sys.argv[1]=="-m":
            if len(sys.argv)>=3:
                mod=sys.argv[2]
                del sys.argv[1:3]
                runpy._run_module_as_main(mod)
            else:
                print("PyShell:\n用法:pyshell -m 模块名称\n运行一个模块。")
        else:
            filename=os.path.realpath(sys.argv[1])
            run_file(filename)
        return

    print("PyShell v%s"%__version__)
    if not in_pythonw():
        try:
            import console_tool
            c=console_tool.Console()
            c.colorize()
            c.title(_TITLE)
            input=c.input
        except:
            c = None
            input=__builtins__.input
            os.system("title %s"%_TITLE) # 设置命令行窗口标题
    else:
        c=None
        input=__builtins__.input

    line=1
    while True:
        try:
            if sys.stdin.closed:
                return
            code=input(">>> ")

            if c is not None:
                c.title("{} - {}".format(_TITLE,code))

            exec_code(code,line)
            line+=1

            if c is not None:
                c.title(_TITLE)

        except KeyboardInterrupt:
            msg="\n^C确实要退出吗?(Y/N) "
            if ask_for_exit(c)==0:
                return
        except EOFError:break

if __name__=="__main__":main()
