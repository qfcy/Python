import sys,os
try:
    from ulang.runtime.main import main
except ImportError:
    # 直接双击运行__main__.py
    try:
        sys.path.remove(os.getcwd())
    except:pass
    sys.path.append(os.path.split(os.getcwd())[0])
    from ulang.runtime.main import main

if sys.argv[0].endswith('__main__.py'):
    sys.argv[0]='python -m ulang'

if __name__=="__main__":main()