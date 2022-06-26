from requests import get
import re,pprint

headers = {
"User-Agent": """Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 \
(KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"""
}

url = input('输入文章网址: ')
req = get(url,headers=headers)
text=req.content.decode('utf-8')
patt=re.compile('<article.*</article>',re.S)
css_patt=re.compile('<link rel="stylesheet" href=".*?blog.*?"',re.S)

title=re.findall('<title>(.*?)</title>',text,re.S)[0]
content='<html><head><title>%s</title><body>'%title
for css in re.findall(css_patt,text):
    content+=css+'>'

content += re.findall(patt,text)[0]
content += '</body></html>'

# 去除文件名不能包含的特殊字符
filename = '%s.html'%title.replace("(","").replace(")","").replace(":","")
with open(filename,'w',encoding='utf-8') as f:
    f.write(content)
