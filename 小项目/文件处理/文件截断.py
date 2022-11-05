import sys,os,traceback

def normpath(path):
    path=os.path.normpath(path).strip('"')
    if path.endswith(':'):
        path += '\\'
    return path

exc=False
if len(sys.argv)<2:
    sys.argv.append(input('输入文件名或拖曳文件:'))
print('输入各文件大小:')
for arg in sys.argv[1:]:
    arg=normpath(arg)
    size=int(input(arg+':'))
    try:
        with open(arg,'rb+') as f:
            f.truncate(size)
    except Exception:
        traceback.print_exc()
        exc=True

if exc:input()
