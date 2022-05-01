"读取文件的程序"
import sys,os,console_tool

PROMPT="文件名:"
def read(filename,encoding="utf-8",errors="replace"):
    "读取文件,并对文件内容进行编码"
    f=open(filename,"rb")#打开文件
    return str(f.read(),encoding=encoding,errors="replace")
def _handle(err,console):
    "输出错误原因"
    console.ctext(err,"red",None,"bold")

def main():
    c=console_tool.Console()#创建Console(控制台)对象
    if len(sys.argv)>1:#如果有系统参数
        for arg in sys.argv[1:]:
            if not( arg.startswith('/') or arg.startswith('-') ):
                try:
                    print(PROMPT+arg)
                    #replace作用:清除字符串中的振铃符,防止输出文件内容时发出响铃声
                    print(read(arg).replace('\x07',''))
                    print()
                except OSError as err:_handle(err)

    while True:#使程序永远循环
        try:
            filename=input(PROMPT)
            if filename.strip():
                content=read(filename).replace('\x07','')
                print(content)
                if filename[len(filename)-2:len(filename)]=="py":
                    c.ctext("\n该文件为python脚本,是否执行?(输入:Y/N)",
                            "blue",None,"bold",end="")
                    if input().lower()=='y':
                        returnval=os.system(filename)#执行该文件
                        if returnval==1:c.ctext("\n执行失败","red",None,"bold")
        except OSError as err:#处理错误
            if filename.lower()=="quit" or filename.lower()=="q":
                c.ctext("Bye!","green")
                return 0
            _handle(err,c)#输出错误原因

if __name__=="__main__":sys.exit(main())
