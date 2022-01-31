import sys,os

if not "idle" in sys.path[1]:#如果程序不在idle中运行
    os.system("title 执行系统命令")#就设置命令行窗口标题
while True: #使程序永远循环
    cmd=input("命令:")
    os.system(cmd)#执行命令
