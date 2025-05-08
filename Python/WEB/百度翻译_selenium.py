# 代码基于网络改写、增加
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time,traceback

def translate(string):
    global prev_result
    if not completed:
        raise Exception("页面未加载完成")
    # 输入要翻译的文本。注意未登录时原文最多为1000字，超出的不会翻译(已登录后为5000字)
    input_element = driver.find_element(By.ID, 'baidu_translate_input')
    input_element.clear()
    input_element.send_keys(string)

    # 点击翻译按钮
    translate_button = driver.find_element(By.ID, 'translate-button')
    translate_button.click()

    # 等待结果出现
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'ordinary-output.target-output.clearfix')))
    # 等待新的结果变化
    while driver.find_element(By.CLASS_NAME, 'ordinary-output.target-output.clearfix').text==prev_result:
        time.sleep(0.05)#pass

    # 获取翻译结果
    output_element = driver.find_element(By.CLASS_NAME, 'ordinary-output.target-output.clearfix')
    output_text = output_element.text
    prev_result=output_text

    # 输出翻译结果
    return output_text

driver_path = r"D:\Users\Administrator\msedgedriver.exe"
completed=False
prev_result=""

# 初始化Chrome浏览器驱动
driver = webdriver.Edge(executable_path=driver_path)

# 打开百度翻译网页
# 百度翻译网址构成：https://fanyi.baidu.com/#<源语种>/<目标语种>/<初始原文>
# 常用语种缩写：中文:zh,英语:en,日语:jp,韩语:kor,粤语:yue,俄语:ru,德语:de,法语:fra
#               泰语:th,葡萄牙语:pt,西班牙语:spa,阿拉伯语:ara,自动检测:auto
from_lang="en"
to_lang="zh"
driver.get('https://fanyi.baidu.com/#%s/%s' % (from_lang,to_lang))

# 等待页面加载完成
wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.ID, 'baidu_translate_input')))
completed=True

# （自己新增）点击关闭提示按钮
close_btn=driver.find_element(By.CLASS_NAME, 'app-guide-close')
close_btn.click()

try:
    while True:
        s=input("输入原文：")
        if s.strip():
            print("翻译结果："+translate(s))
finally:
    driver.quit()