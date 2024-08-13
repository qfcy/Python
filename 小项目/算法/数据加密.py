"命令行: 数据加密.py 文件名1 [文件名2] [...]"
import hashlib,sys,os,zlib
__all__=["encrypt","decrypt","test"]
FILETYPE=".encrypt"

def encrypt(data,password,compress_level=-1):
    data = zlib.compress(data,compress_level) # 先使用zlib压缩
    sha256=hashlib.sha256(password.encode("utf-8")).hexdigest() # 获取密码的sha256
    head = sha256.encode() + len(data).to_bytes(8,"big") # 文件头
    mask = hashlib.sha256((password*2).encode("utf-8")
                          ).hexdigest() # 使用密码的变体(重复2次)的sha256作为掩码
    mask_num = int.from_bytes(mask.encode(),"little")

    encrypted=b''
    for i in range(0,len(data),64): # sha256结果为64字节长
        num = int.from_bytes(data[i:i+64],"little") # 截取data的一部分
        num_enc = num ^ mask_num # 将data的一部分与掩码进行异或运算
        encrypted += num_enc.to_bytes(64,"little")

    return head + encrypted[:len(data)]

def decrypt(encrypted,password):
    sha256 = encrypted[:64]
    if hashlib.sha256(password.encode("utf-8")).hexdigest().encode()\
                   != sha256: # 检验密码是否正确
        raise TypeError("Invalid password")

    mask = hashlib.sha256((password*2).encode("utf-8")).hexdigest() # 掩码
    mask_num = int.from_bytes(mask.encode(),"little")
    length = int.from_bytes(encrypted[64:64+8],"big") # (压缩的)数据长度

    data = b''
    for i in range(64+8,len(encrypted),64):
        num_enc = int.from_bytes(encrypted[i:i+64],"little")
        num = num_enc ^ mask_num # 与掩码进行异或运算
        data += num.to_bytes(64,"little")

    return zlib.decompress(data[:length]) # 返回原长度的数据

def test():
    seq=b"Hello world!";password="123"
    assert decrypt(encrypt(seq,password),password)==seq

def __ask_replace(filename):
    if not os.path.isfile(filename):return True
    result=input("文件 %s已存在,要替换它吗? (Y/N) "%filename)
    return result.lower().startswith('y')
def main():
    if len(sys.argv)==1:
        print("""%s\n未提供文件。"""%__doc__);return
    for arg in sys.argv[1:]:
        print("处理文件 "+arg)

        with open(arg,'rb') as fin:
            if arg.lower().endswith(FILETYPE):#解密
                newfile = arg[:-len(FILETYPE)]
                if not __ask_replace(newfile):continue
                password = input("输入密码: ")
                data = decrypt(fin.read(),password)
            else: #加密
                newfile = arg + FILETYPE
                if not __ask_replace(newfile):continue
                password = input("输入密码: ")
                data = encrypt(fin.read(),password)

            with open(newfile,"wb") as fout:
                fout.write(data)

if __name__=="__main__":main()
