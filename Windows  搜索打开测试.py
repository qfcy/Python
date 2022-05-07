import subprocess
from urllib.parse import quote
kw = input("输入搜索词: ")
path = input("输入路径: ")
url = 'search-ms:displayname=Python&crumb=&crumb=System.Generic.String:%s&crumb=location:%s'%(quote(kw),quote(path))
print(url)
subprocess.run(["explorer.exe",'/root,',url])
input()