# http文件服务器程序, 可用于在本地创建一个网站，基于socket库
# 使用方法：将本文件"http文件服务器.py"和html文件(如:index.html)放在同一个目录
# 然后运行"http文件服务器.py"即可
# 命令行：python http文件服务器.py <端口号(可选)>

import socket, sys, os, time, traceback, pprint
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import parse_qs, unquote
import chardet,mimetypes

HEAD_100 = b"HTTP/1.1 100 Continue\n"
HEAD_OK = b"HTTP/1.1 200 OK\n"
HEAD_206 = b"HTTP/1.1 206 Partial Content\n"
HEAD_404 = b"HTTP/1.1 404 Not Found\n"
RECV_LENGTH = 16384 # sock.recv()一次接收内容的长度
CHUNK_SIZE = 1<<19 # 0.5MB
SEND_SPEED = 10 # 大文件的发送速度限制，单位为MB/s，设为非正数则不限速

def _read_file_helper(head,file,chunk_size,start,end): # 分段读取文件使用的生成器
    yield head
    file.seek(start)
    total=0
    while total<end-start:
        size=min(chunk_size,end-start-total)
        data=file.read(size)
        total+=size
        yield data
    file.close()
def _slice_helper(data,size):
    n=len(data)
    for i in range(0,n,size):
        yield data[i:i+size]
def convert_bytes(num): # 将整数转换为数据单位
    units = ["", "K", "M", "G", "T", "P", "E", "Z", "Y"]

    for unit in units:
        if num < 1024:
            return f"{num:.2f}{unit}B"
        num /= 1024
    return f"{num:.2f}{units[-1]}B"

def check_filetype(path): # 检查文件扩展名并返回content-type
    mime_type=mimetypes.guess_type(path)[0]
    if mime_type is None: # 未知类型
        return b"" # 不返回类型，由浏览器自行检测
    if mime_type.lower().startswith("text"):
        with open(path,"rb") as f:
            head=f.read(512) # 读取文件头部，并检测编码
            detected=chardet.detect(head)
            coding=detected["encoding"]
            if coding=="ascii": # 如果未检测到多字节的编码，则尝试继续检测
                data=f.read(3072)
                if data:
                    detected=chardet.detect(data)
                    coding=detected["encoding"]
        if coding is not None and detected["confidence"]>0.9:
            mime_type+=";charset=%s"%coding
    return b"Content-Type: %s\n"%mime_type.encode()

def parse_head(req_head): # 解析请求头中的路径和查询参数
    path = unquote(req_head.split(' ')[1])[1:] # 获取请求url后面的路径, 在请求数据第一行
    split = path.rsplit("#",1)
    path = split[0]
    fragment = split[1] if len(split)==2 else None
    split = path.split("?",1)
    dir = split[0]
    query = parse_qs(split[1],keep_blank_values=True) if len(split)==2 else {}
    if dir == "": # 路径为空，则用当前路径
        dir="."
    dir=dir.replace("\\","/")
    if dir[-1]=="/": # 去除末尾多余的斜杠
        dir=dir[:-1]
    return dir,query,fragment

def get_dir_content(dir):
    path = os.path.join(os.getcwd(),dir)
    head = HEAD_OK
    response = head + f"""
<html><head>
<meta http-equiv="content-type" content="text/html;charset=utf-8">
<title>{path} 的目录</title>
</head><body>
<h1>{path}的目录</h1><p></p>""".encode()
    # 获取当前路径下的各个文件、目录名
    subdirs=[] # 子目录名
    subfiles=[] # 子文件名
    for sub in os.listdir(path):
        # os.listdir()无法直接区分目录名和文件名, 因此还需进行判断
        if os.path.isfile(os.path.join(path,sub)): # 如果子项是文件
            subfiles.append(sub)
        else: # 子项是目录
            subdirs.append(sub)
    subdirs.sort(key=lambda s:s.lower()) # 升序排序
    subfiles.sort(key=lambda s:s.lower())

    if dir != ".":
        response += f'\n<a href="/{dir}/..">[上级目录]</a><p></p>'.encode()
    # 依次显示各个子文件、目录
    for sub in subdirs:
        response += f'\n<a href="/{dir}/{sub}">[目录]{sub}</a><p></p>'.encode()
    for sub in subfiles:
        size=convert_bytes(os.path.getsize(os.path.join(path,sub)))
        response += f'''\n<a href="/{dir}/{sub}">{sub}</a>\
<span style="color: #707070;">&nbsp;{size}</span><p></p>'''.encode()
    response += b"\n</body></html>"
    return response

def get_file(path,start=None,end=None): # 返回文件的数据
    size = os.path.getsize(path)
    if start is not None or end is not None:
        start = start or 0
        end = end or size
        head = HEAD_206 + check_filetype(path)
        head += b"Content-Range: bytes %d-%d/%d\n\n" % (start,end,size)
    else:
        start = 0; end = size
        head = HEAD_OK + check_filetype(path) # 加入content-type
        # 响应头末尾以两个换行符(\n\n)结尾
        head += b"Content-Length: %d\n\n" % size # 加入文件长度
    return _read_file_helper(head,open(path,'rb'),CHUNK_SIZE,start,end) # 分段读取文件

def getcontent(dir,start=None,end=None): # 根据url的路径dir构造响应数据
    # 将dir转换为系统路径, 放入path
    path = os.path.join(os.getcwd(),dir)
    try:
        if ".." in dir.split("/"): # 禁止访问上层目录
            raise OSError # 引发错误, 进入except语句
        if os.path.isdir(path):
            # 找出路径中名为index的文件，若有则直接读取
            file=None
            for f in os.listdir(path):
                if f.split(".")[0].lower()=="index":
                    file = f
                    if f.split(".")[1].lower() in ("htm","html"): # 当有多个index文件时html文件优先
                        break
            if file is not None:
                path = os.path.join(path,file)

        # 构造响应数据
        if os.path.isfile(path): # --path是文件, 就打开文件并读取--
            response = get_file(path,start,end)

        elif os.path.isdir(path): # --path是路径, 就显示路径中的各个文件--
            response = get_dir_content(dir)

        else: # 不存在文件或目录
            # 若.html的后缀名省略，自动寻找html文件
            # 不过，例如要访问path，path/index.html要优先于path.html，用户可自行修改
            for ext in (".htm",".html"):
                file = path + ext
                if os.path.isfile(file):
                    response = get_file(file,start,end)
                    break
            else:
                raise OSError # 当作错误处理, 进入except语句

    except OSError:
        # 返回404
        response = HEAD_404 + f"""
<html><head>
<meta http-equiv="content-type" content="text/html;charset=utf-8">
<title>404</title>
</head><body>
<h1>404 Not Found</h1>
<p>来自 Python 服务器测试</p>
<a href="/{dir}/..">返回上一级</a>
<a href="/">返回首页</a>
</body></html>
""".encode()
    return response

def send_response(sock,response,address):
    # 分段发送响应
    if isinstance(response,bytes):
        response = _slice_helper(response,CHUNK_SIZE)
    total=0
    chunk=next(response)
    sock.send(chunk)
    begin=time.perf_counter()
    while True:
        size=len(chunk)
        total+=size
        try:
            chunk=next(response)
        except StopIteration:
            break
        else:
            if SEND_SPEED > 0:
                seconds = (total/(1<<20))/SEND_SPEED - \
                          (time.perf_counter() - begin) # 预计时间 - 实际时间
                if seconds > 0:
                    time.sleep(seconds) # 延迟发送，限制速度
        sock.send(chunk)
    if SEND_SPEED > 0 and total >= SEND_SPEED*(1<<20) \
        or SEND_SPEED <= 0 and total >= 1<<27: # 如果预计发送时间超过1秒，或不限速时大于128MB
        print(address,"较大响应 (%s) 发送完毕" % convert_bytes(total))

def handle_post(sock,req_head,req_info,content):
    length = int(req_info.get('Content-Length',-1))

    if not (content.startswith(b"------WebKitFormBoundary") and \
        len(content)<=42): # 如果表单未以WebKitFormBoundary结束
        if len(content)<length: # 第一次调用sock.recv接收的内容不完整，就尝试继续接收数据
            while True:
                new_data = sock.recv(RECV_LENGTH)
                content += new_data
                if not new_data or len(content)>=length:break
            #content += sock.recv(length-len(content))
        if length != -1:content = content[:length] # 截断过长的数据

    if content.startswith(b"------WebKitFormBoundary"): # 处理上传文件等请求
        if len(content)<=42: # 空的表单
            content = b''
        else:
            split=content.splitlines()[1:-1]
            content = b"\n".join(split) # 去除第一行和末尾的WebKitFormBoundary标识
        print(address,"提交文件数据:",content)
    else:
        if len(content)<length: # post含有多个tcp数据包时
            return HEAD_100 # 让客户端继续发送数据
        else:
            form=parse_qs(content.decode("utf-8"),
                          keep_blank_values=True,encoding="utf-8")
            print(address,"提交数据:",form)

    #dir=parse_head(req_head)[0]
    return HEAD_OK + """
<html><head>
<meta http-equiv="content-type" content="text/html;charset=utf-8">
<title>提交成功</title>
</head><body>
<h1>提交成功</h1>
<a href="javascript:void(0);"
onclick="window.history.back();">返回</a>
</body></html>
""".encode()

def get_request_info(data):
    # 获取请求头部信息，首行存入req_head，其他信息存入字典req_info
    lines = data.splitlines()
    req_head = lines[0]
    req_info = {}
    for line in lines[1:]:
        lst = line.split(':', 1)
        try:
            key, value = lst[0].strip(), lst[1].strip()
            req_info[key] = value
        except (ValueError, IndexError): # 不是请求头信息时
            pass
    return req_head,req_info

def handle_get(req_head,req_info):
    url=unquote(req_head.split(' ')[1])
    dir=parse_head(req_head)[0]
    if "Range" in req_info: # 断点续传
        range_=req_info["Range"].split("=",1)[1]
        start,end=range_.split("-")
        start = int(start) if start else None
        end = int(end) if end else None
        print(address,"访问URL: %s (从 %s 到 %s 断点续传)" % (url,
            convert_bytes(start) if start is not None else None,
            convert_bytes(end) if end is not None else "末尾"))
        return getcontent(dir,start,end)
    else:
        print(address,"访问URL:",url)
        return getcontent(dir) # 获取目录的数据

def handle_client(sock, address):# 处理客户端请求
    raw = sock.recv(RECV_LENGTH)
    data = raw.decode("utf-8")
    if data=="":return # 忽略空数据

    req_head,req_info=get_request_info(data)
    #print("请求数据:", req_head);pprint.pprint(req_info)

     # 获取响应数据，response可以为bytes类型，或一个生成器
    if req_head.startswith("POST"): # POST请求
        response=handle_post(sock,req_head,req_info,raw.splitlines()[-1])
    else: # GET请求
        response=handle_get(req_head,req_info)

    try:send_response(sock,response,address) # 向客户端分段发送响应数据
    except ConnectionError as err:
        print(address,"连接异常 (%s): %s" % (type(err).__name__,str(err)))
    sock.close() # 关闭客户端连接

def handle_client_thread(*args,**kw): # 仅用于多线程中产生异常时输出错误信息
    try:handle_client(*args,**kw)
    except Exception:
        traceback.print_exc()

PORT=int(sys.argv[1]) if len(sys.argv)==2 else 80 # 80为HTTP的默认端口
if __name__ == "__main__":
    host = socket.gethostname()
    ips = socket.gethostbyname_ex(host)[2] # 或者socket.gethostbyname(host)
    print("服务器的IP:",ips)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("", PORT))
    sock.listen(128) # 监听，参数为最大等待连接数
    import webbrowser
    webbrowser.open('http://127.0.0.1:%d/'%PORT)

    # 单线程模式，一次处理一个客户端
    #while True:
    #    client_sock, address = sock.accept()
    #    handle_client(client_sock, address)
    # 多线程
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        while True:
            client_sock, address = sock.accept()
            executor.submit(handle_client_thread, client_sock, address)
    sock.close()
