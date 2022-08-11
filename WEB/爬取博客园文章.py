from requests import get
from lxml.etree import HTML, tostring
import re

headers = {
"User-Agent": """Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 \
(KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"""
}

url = input('输入文章网址: ')
req = get(url,headers=headers)
text=req.content.decode('utf-8')

title = re.findall('<title>(.*?)</title>',text,re.S)[0]
tree = HTML(text)
div = tree.xpath('//*[@id="cnblogs_post_body"]')[0]

content='<html><head><title>%s</title><body>'%title
for result in re.findall('(<link.*?rel="stylesheet" href="(.*?)")',text,re.S):
    if not result[1].startswith('https://'):
        css = result[0].replace(result[1],
                                'https://www.cnblogs.com'+result[1]) + '>'
    else:
        css = result[0] + '>'
    content += css

content += tostring(div, method='html').decode('utf-8')
content += '</body></html>'
with open('%s.html'%title,'w',encoding='utf-8') as f:
    f.write(content)
