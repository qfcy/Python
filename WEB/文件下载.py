import os
import requests
import time
import sys
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import unquote,urlparse
from timer_tool import Timer

CHUNK_SIZE = 1 << 16
WAIT_TIME = 10
OUTPUT_INTERVAL=1

def convert_size(num): # 将整数转换为数据单位
    units = ["", "K", "M", "G", "T", "P", "E", "Z", "Y"]

    for unit in units:
        if num < 1024:
            return f"{num:.2f}{unit}B"
        num /= 1024
    return f"{num:.2f}{units[-1]}B"

_used_filenames=set()
def extract_filename(url):
    # 从 URL 中提取文件名并进行解码
    path=urlparse(unquote(url)).path
    filename = os.path.basename(path)
    if filename in _used_filenames:
        i=1
        while True:
            split=os.path.splitext(filename)
            new_filename=f"{split[0]}_{i}{split[1]}"
            if new_filename not in _used_filenames:break
            i+=1
        filename=new_filename
    _used_filenames.add(filename)
    return sanitize_filename(filename)

def download_file(url, local_filename):
    # 检查本地文件是否存在，获取已下载的字节数
    resume_header = {}

    while True:
        try:
            if os.path.exists(local_filename):
                size=os.path.getsize(local_filename)
                resume_header['Range'] = f'bytes={size}-'
                print(f"继续下载: {url} 到 {local_filename}")
            else:
                size=0 # 开始下载时，已下载的大小
                print(f"开始下载: {url} 到 {local_filename}")

            size_delta=0 # 新下载的大小
            t=Timer();pre_time=0

            # 发起请求，支持断点续传
            response = requests.get(url, headers=resume_header, stream=True)
            response.raise_for_status()  # 检查请求是否成功

            # 以追加模式打开文件
            with open(local_filename, 'ab') as f:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    size_delta+=len(chunk)
                    if chunk:  # 过滤掉空块
                        f.write(chunk)

                    cur_time=t.gettime()
                    if cur_time // OUTPUT_INTERVAL - pre_time // OUTPUT_INTERVAL >= 1:
                        print(f"""{local_filename} 已下载 \
{convert_size(size+size_delta)} {convert_size(size_delta/cur_time)}/s""")
                        pre_time=cur_time

            print(f"下载完成: {local_filename} 用时: {t.gettime()}s")
            break  # 下载完成，退出循环

        except Exception as err:
            print(f"下载失败 (已下载 {convert_size(size+size_delta)}): {err} ({type(err).__name__})")
            print(f"{WAIT_TIME}s后尝试重新连接...")
            time.sleep(WAIT_TIME)  # 等待 10 秒后重试

def sanitize_filename(filename):
    # 去掉文件名中的非法字符
    return filename.translate(str.maketrans('', '', '\\/:*?"<>|'))


def show_help():
    print(f"Usage: python {sys.argv[0]} url_or_urlfile1 -o file1 url_or_urlfile2 -o file2 ...""")

def main():
    if len(sys.argv)<2:
        show_help()
        return

    urls_and_outputs=sys.argv[1:]

    # 解析 URL 和输出文件名
    url_output_pairs = []; other_urls = []
    i = 0
    while i < len(urls_and_outputs):
        url_file = urls_and_outputs[i]
        if not "://" in url_file:
            with open(url_file,encoding="utf-8") as f:
                url=f.readline().strip()
                # 读取剩下的行 (如果有剩下的行，不能用-o参数)
                other_urls=[url_line.strip() for url_line in f.readlines() if url_line.strip()]
        else:
            url=url_file # 直接传入了URL作为参数
        if i + 1 < len(urls_and_outputs) and urls_and_outputs[i + 1] == '-o':
            if i + 2 >= len(urls_and_outputs): # -o之后没有文件名
                show_help()
                return
            output_file = urls_and_outputs[i + 2]
            url_output_pairs.append((url, output_file)) # 会忽略other_urls
            i += 3  # 跳过 url, -o, file
        else:
            # 如果没有指定输出文件名，则从 URL 中提取文件名
            url_output_pairs.append((url, extract_filename(url)))
            for url_line in other_urls:
                url_output_pairs.append((url_line, extract_filename(url)))
            i += 1  # 只跳过 url

    # 创建线程池并下载每个 URL
    with ThreadPoolExecutor() as executor:
        futures = []
        for url, output_file in url_output_pairs:
            futures.append(executor.submit(download_file, url, output_file))

        # 等待所有线程完成
        for future in futures:
            future.result()  # 处理异常（如果有的话）

if __name__ == "__main__":main()