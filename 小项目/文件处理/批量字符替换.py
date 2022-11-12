import os,search_file
xd1="xd34".encode('ansi')
xd2="xd34".encode('utf-8')
bd1="百度".encode('ansi')
bd2="百度".encode('utf-8')
yx=b' "%__email__'
yx1="邮箱".encode('utf-8')
yx2="邮箱".encode('utf-8')
words = [b'3416xxxxxx@qq.com',xd1,xd2,yx]
for file in search_file.direc('.',dirs=False): # 可用os.listdir
    if ".bak" in file.lower() or "字符替换" in file:continue
    with open(file,'rb') as f:
        data=f.read()
    
    flag=False
    for word in words:
        if word in data:
            flag=True
    if flag:
        print('replaced',file)
        data=data.replace(b'3416xxxxxx@qq.com',b'3076711200@qq.com')\
              .replace(xd1,b'qfcy_').replace(xd2,b'qfcy_')
        if file.lower().endswith('.py') or file.lower().endswith('.pyw'):
            data=data.replace(yx,b'"')
        try:os.rename(file,file+'.bak')
        except OSError:
            os.rename(file,file+'(2).bak')
        with open(file,'wb') as f:
            f.write(data)
    if yx1 in data or yx2 in data and (file.lower().endswith('.py') or file.lower().endswith('.pyw')):
        print('email',file)
