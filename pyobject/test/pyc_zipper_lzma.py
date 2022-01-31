# 使用lzma的pyc文件压缩、保护工具
import sys,marshal,lzma
from inspect import iscode
from pyobject.code_ import Code
try:
    from importlib._bootstrap_external import MAGIC_NUMBER
except ImportError:
    from importlib._bootstrap import MAGIC_NUMBER

def dump_to_pyc(pycfilename,code):
    c=Code()
# 反汇编的co_code
##2     0 LOAD_CONST               0 (455)
##      2 LOAD_CONST               1 (None)
##      4 IMPORT_NAME              0 (lzma)
##      6 STORE_NAME               0 (lzma)
##      8 LOAD_CONST               0 (455)
##     10 LOAD_CONST               1 (None)
##     12 IMPORT_NAME              1 (marshal)
##     14 STORE_NAME               1 (marshal)
##
##3    16 LOAD_NAME                2 (exec)
##     18 LOAD_NAME                1 (marshal)
##     20 LOAD_METHOD              3 (loads)
##     22 LOAD_NAME                0 (lzma)
##     24 LOAD_METHOD              4 (decompress)
##     26 LOAD_CONST               2 (数据)
##     28 CALL_METHOD              1
##     30 CALL_METHOD              1
##     32 CALL_FUNCTION            1
##     34 RETURN_VALUE
    c.co_code=b'''d\x00d\x01l\x00Z\x00d\x00d\x01l\x01Z\x01e\x02\
e\x01\xa0\x03e\x00\xa0\x04d\x02\xa1\x01\xa1\x01\x83\x01\x01\x00d\x01S\x00'''
    c.co_names=('lzma', 'marshal', 'exec', 'loads', 'decompress')
    #也可换成bz2,lzma等其他压缩模块
    c.co_consts=(0, None,lzma.compress(marshal.dumps(code._code)))
    c.co_flags=64
    c.co_stacksize=6
    with open(pycfilename,'wb') as f:
        # 写入 pyc 文件头
        if sys.winver >= '3.7':
            pycheader=MAGIC_NUMBER+b'\x00'*12
        else:
            pycheader=MAGIC_NUMBER+b'\x00'*8
        f.write(pycheader)
        # 写入bytecode
        marshal.dump(c._code,f)

def process_code(co):
    co.co_lnotab = b''
    if co.co_code[-4:]!=b'S\x00S\x00':
        co.co_code += b'S\x00'
    co.co_filename = ''
    #co.co_name = ''
    co_consts = co.co_consts
    for i in range(len(co_consts)):
        obj = co_consts[i]
        if iscode(obj):
            data=process_code(Code(obj))
            co_consts = co_consts[:i] + (data._code,) + co_consts[i+1:]
    co.co_consts = co_consts
    return co

if len(sys.argv) == 1:
    print('Usage: %s [filename]' % sys.argv[0])

for file in sys.argv[1:]:
    data=open(file,'rb').read()
    data=data[16:] if data[16]==227 else data[12:]
    co = Code(marshal.loads(data))

    process_code(co)
    dump_to_pyc(file,co)
    print('Processed:',file)
