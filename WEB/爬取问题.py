from requests import get
from lxml.etree import HTML, tostring
import time

def update(print_new = True):
    global lst,lst_new
    headers = {
    "User-Agent": """Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 \
    (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"""
    }

    url = "https://ask.csdn.net/ask"
    req = get(url,headers=headers)
    text=req.content.decode('utf-8')

    tree = HTML(text)
    ques = tree.xpath('//*[@id="floor-ask-content-index_493"]/div/div/div[2]/div/div/div[1]/a/h2')
    lst_new=[]
    for q in ques:
        lst_new.append(q.text)
        if q.text not in lst and print_new:
            print("新问题: ",q.text)

    lst = lst_new.copy()

lst=[]
lst_new=[]
update(print_new = False) # 首次运行更新列表
time.sleep(5)
while True:
    update()
    time.sleep(8)