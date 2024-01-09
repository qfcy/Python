import sys,os,time,traceback
if len(sys.argv) == 1: # 用户未提供程序参数
    # Windows的控制台窗口支持直接拖入文件
    file = os.path.normpath(
            input('将一个文件拖到这里 (或输入文件路径),再按Enter: ')
            ).strip('"')
    files=[file]
    while True:
        str = input('将一个文件拖到这里 (或输入文件路径),再按Enter。直接按Enter可进入下一步: ')
        if not str.strip():break
        file = os.path.normpath(str).strip('"')
        files.append(file)
else:
    files=sys.argv[1:]

# 实测Windows系统能显示的最大时间: 2108 01 01 (07:59:58)
format = "%Y.%m.%d %H:%M"
time_ = input('输入新的修改日期(格式例如 2023.4.30 21:33)，再回车: ')
for file in files:
    try:
        os.utime(file,
                 (time.mktime(time.strptime(time_, format)),)*2)
        print("修改成功:",file)
    except Exception:
        traceback.print_exc() # 输出错误信息

input("按Enter键继续 ..")


