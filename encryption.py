#加密程序
__doc__="命令行: encryptions.py 文件名1 [文件名2] [...]"

__all__=["encrypt","decrypt","test"]
DELTA=100
FILETYPE=".encrypt"
def encrypt(bytes,delta=DELTA):
    for i in reversed(bytes):
        if i<256-delta:i+=delta
        else:i-=256-delta
        yield i

def decrypt(bytes,delta=DELTA):
    for i in reversed(bytes):
        if i<delta:i+=256-delta
        else:i-=delta
        yield i

def test():
    seq=bytes(range(256))
    encrypted=bytes(encrypt(seq))
    assert bytes(decrypt(encrypted))==seq

def __ask_replace(filename):
    result=input("文件%s已存在,要替换它吗? "%filename)
    return result.lower().startswith('y')
def main():
    import sys,os
    verbose="-v" in sys.argv

    if len(sys.argv)>1:
        for arg in sys.argv[1:]:
            if arg.startswith('-') or arg.startswith('/'):continue
            
            fin=open(arg,'rb')
            if arg.endswith(FILETYPE):#解密
                newfilename=arg[:-len(FILETYPE)]
                if os.path.isfile(newfilename):
                    if not __ask_replace(newfilename):continue
                print("正在解密 %s"%arg)
                fout=open(newfilename,'wb')
                fout.write(bytes(decrypt(fin.read())))
            else: #加密
                print("正在加密 %s"%arg)
                fout=open(arg+FILETYPE,"wb")
                fout.write(bytes(encrypt(fin.read())))
            fout.close()
    else:
        print("""%s\n未提供文件。"""%__doc__)

if __name__=="__main__":main()
