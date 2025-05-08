import sys,os, traceback,marshal,builtins, warnings, platform
import runpy
try: # 用于打开pyc文件
    from importlib._bootstrap_external import MAGIC_NUMBER
except ImportError:
    from importlib._bootstrap import MAGIC_NUMBER # Python 3.4等较低版本

# 默认的环境变量
vars_={"__annotations__":{},"__builtins__":__builtins__,"__doc__":None,
      "__loader__":__loader__,"__name__":"__main__","__package__":None,
      "__spec__":None}
_TITLE="PyShell"
__version__="1.3.3"

def exec_code(code,line=0):
    # 执行一行输入的代码
    try:
##        result=eval(code,vars_) # 旧版:尝试使用exec或eval, eval优先
##        builtins._ = result
##        if result is not None:print(repr(result))
##    except SyntaxError:
##        try:
##            exec(code,vars_)
##        except BaseException as err:
##            try:raise err from None
##            except:handle()
        if code.strip():
            try:co=compile(code,'<PyShell #{}>'.format(line),'single')
            except SyntaxError:
                co=compile(code,'<PyShell #{}>'.format(line),'exec')
            exec(co, vars_)
    except BaseException:handle()

def run_file(filename):
    code=open(filename,'rb').read()
    if filename.lower().endswith(".pyc"):
        if code[:4] != MAGIC_NUMBER:
            warnings.warn("警告: Pyc文件头不匹配。")
        code=code[16:] if code[16]==227 else code[12:]
        code=marshal.loads(code)
    else:
        code=code.decode(encoding='utf-8').strip('\ufeff')
    backup=sys.argv
    sys.argv=sys.argv[1:] # 除去原本的sys.argv[0]这个参数
    sys.path.append(os.path.split(filename)[0])
    vars_["__file__"]=filename
    try:
        if isinstance(code,str):
            co=compile(code,filename,"exec")
        else:
            co=code
        exec(co,vars_)
    except BaseException:handle()
    sys.argv=backup

def interactive():
    print("PyShell v%s (Python %s)"%(__version__, platform.python_version()))
    if not in_pythonw():
        try:
            import console_tool # 初始化console标题, 颜色等
            c=console_tool.Console()
            c.colorize()
            c.title(_TITLE)
            input=c.input
        except:
            c = None
            input=builtins.input
            os.system("title %s"%_TITLE)
    else:
        c=None
        input=__builtins__.input

    lineno=1
    while True:
        try:
            if getattr(sys.stdin,"closed",False): # 其他代码请求了退出Python
                return
            code=input(">>> ")

            if c is not None:
                c.title("{} - {}".format(_TITLE,code))

            exec_code(code,lineno)
            lineno+=1

            if c is not None:
                c.title(_TITLE)

        except KeyboardInterrupt:
            if ask_for_exit(c)==0:
                return
        except EOFError:break

def in_pythonw(): # 判断是否为pythonw(无控制台窗口)的环境
    return "pythonw.exe" in sys.executable or "pyshell_w.exe" in sys.executable

def handle():
    traceback.print_exc()

def ask_for_exit(console=None):
    msg="\n^C确实要退出吗?(Y/N) "
    if console:console.ctext(msg,"green",None,"bold",end='')
    else:print(msg,end='')
    try:
        if input().lower().startswith('y'):return 0
    except KeyboardInterrupt:
        return ask_for_exit(console)

def help():
    print("""用法 Usage:\n
    pyshell 某py,pyw或pyc文件路径: 运行脚本。
    pyshell -c <Python代码> : 运行指定的Python指令。
    pyshell -m <模块名称> : 运行一个模块。
    pyshell -i <其他参数>: 运行脚本或模块后进入交互模式, 建议用于调试python脚本。
    pyshell --no-autoexec <其他参数>: 不自动运行autoexec.py。
    pyshell -h (或 /?): 显示此帮助信息。
    不带参数: 直接进入交互模式。
""")

def main():
    # 执行autoexec.py
    if '--no-autoexec' not in sys.argv:
        try:
            if os.path.isfile(sys.argv[0]):
                app_path=sys.argv[0]
            else:
                app_path=sys.executable
            autoexecfile=os.path.split(app_path)[0]+"\\autoexec.py"
            run_file(autoexecfile)
        except BaseException:handle()
    else:sys.argv.remove('--no-autoexec') # 移除该参数，便于处理其他参数
        

    # 处理命令行参数
    if len(sys.argv)>1:
        if sys.argv[1]=="-i":
            debug=True
            del sys.argv[1] # 便于处理其他参数
        else:
            debug=False

        if sys.argv[1]=="-c":
            if len(sys.argv)>=3:# 检查有无提供代码
                code=sys.argv[2]
                sys.argv=[sys.argv[1]]+sys.argv[3:] # 原版python解释器中使用-c时，第一项也为“-c”
                try:exec_code(code)
                except BaseException:handle()
            else:help()

        elif sys.argv[1]=="-m":
            if len(sys.argv)>=3:# 检查有无提供模块名称
                global vars_
                modname=sys.argv[2]
                del sys.argv[1:3]
                try:vars_ = runpy.run_module(modname,init_globals=vars_,
                                             run_name='__main__')
                except BaseException:handle()
            else:help()
        elif sys.argv[1] in ('/?','-?','-h','--help'):
            help()
        else:
            filename=os.path.realpath(sys.argv[1])
            run_file(filename)
        if not debug:return

    interactive()

if __name__=="__main__":main()
