import sys,marshal,traceback
try:
    from importlib._bootstrap_external import MAGIC_NUMBER
except ImportError:
    from importlib._bootstrap import MAGIC_NUMBER

def dump_to_pyc(pycfilename,data):
    with open(pycfilename,'wb') as f:
        # 写入 pyc 文件头
        if sys.winver >= '3.7':
            pycheader=MAGIC_NUMBER+b'\x00'*12
        else:
            pycheader=MAGIC_NUMBER+b'\x00'*8
        f.write(pycheader)
        # 写入bytecode
        f.write(data)

if len(sys.argv) == 1:
    print('Usage: %s [filename]' % sys.argv[0])

for file in sys.argv[1:]:
    try:
        with open(file,'rb') as f:
            d=f.read()
            d=d[16:] if d[16]==227 else d[12:] # 寻找数据开始的'\xe3'标志
            c=marshal.loads(d)
            modname=c.co_names[0] if len(c.co_names)>=1 else ''
            if modname in ('bz2','lzma','zlib'):
                mod=__import__(modname)
                data=mod.decompress(c.co_consts[2]) # 解压数据
                marshal.loads(data) # 测试解压后数据完整性
                dump_to_pyc(file,data)
                print('Processed:',file)
            else:
                raise TypeError('不是压缩的pyc文件: '+file)
    except Exception:
        traceback.print_exc()
