import sys,os

prompt="命令:"
TITLE="执行系统命令"

def shell(command):
    #忽略异常地执行命令
    os.system("title 执行系统命令 - %s"%command)
    try:os.system(command)#执行命令
    except:pass
    os.system("title %s"%TITLE)

os.system("title %s"%TITLE) #设置命令行窗口标题
if len(sys.argv)>1:
    for arg in sys.argv[1:]:
        #如果参数不是命令行开关
        if not( arg.startswith("-") or arg.startswith("/") ):
            print(prompt+arg)
            shell(arg)

while True: #使程序循环
    try:
        cmd=input(prompt)
        if cmd: #如果用户输入了命令
            #在命令为exit或quit时退出
            if cmd.strip().lower() in ("exit","quit"):
                sys.exit()
            else:shell(cmd)
    except (KeyboardInterrupt,EOFError):
        try:print()
        except:pass