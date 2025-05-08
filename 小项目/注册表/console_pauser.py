# 以管理员身份运行用的辅助脚本，用于不关闭控制台
def main():
    del globals()["main"] # 避免污染全局变量
    import sys,os,traceback
    sys.argv.pop(0) # console_pauser自身
    main_script=sys.argv[0]
    globals()["__file__"]=main_script

    with open(main_script,encoding="utf-8") as f:
        code=f.read()
    exit_code=0
    try:
        exec(compile(code,main_script,"exec"),globals(),globals())
    except SystemExit as err:
        exit_code=err.code
    except BaseException:
        traceback.print_exc()
    os.system("pause")
    sys.exit(exit_code)

main()