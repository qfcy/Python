# http文件服务器程序, 可用于在本地创建一个网站，基于socket库
# 使用方法：将本文件"http文件服务器.py"和html文件(如:index.html)放在同一个目录
# 然后运行"http文件服务器.py"即可

import socket, os, time,traceback,pprint
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import parse_qs,unquote

head_100=b"HTTP/1.1 100 Continue\n"
head_ok = b"HTTP/1.1 200 OK\n"
head_404 = b"HTTP/1.1 404 Not Found\n"
def check_filetype(path): # 检查文件扩展名并返回content-type
    path=path.lower()
    if path.endswith(".htm") or path.endswith(".html"):
        return b"content-type: text/html\n\n"
    elif path.endswith(".css"):
        return b"content-type: text/css\n\n"
    elif path.endswith(".js") or path.endswith(".ts"):
        return b"content-type: application/javascript\n\n"
    else:
        return b"\n"

def parse_dir(req_head): # 解析请求头中的路径
    dir = unquote(req_head.split(' ')[1])[1:] # 获取请求url后面的路径, 在请求数据第一行
    if dir == "":
        dir="."
    if dir[-1] in ("/","\\"): # 去除末尾多余的斜杠
        dir=dir[:-1]
    return dir

def getcontent(dir): # 根据url的路径dir构造响应数据
    # 将dir转换为系统路径, 放入path
    path = os.path.join(os.getcwd(),dir)
    #print("访问路径:",path)
    try:
        if os.path.isdir(path):
            # 找出路径中名为index的文件
            file=None
            for f in os.listdir(path):
                if f.split(".")[0].lower()=="index":
                    file = f
                    if f.split(".")[1].lower() in ("htm","html"): # 当有多个index文件时html文件优先
                        break
            if file != None:
                path = os.path.join(path,file)

        head = head_ok + check_filetype(path) # 加入content-type
        # 构造响应数据
        if os.path.isfile(path): # path是文件, 就打开文件并读取
            with open(path,'rb') as f:
                response = head + f.read()
        elif os.path.isdir(path): # path是路径, 就显示路径中的各个文件
            response = head + (f"""
<html><head>
<meta http-equiv="content-type" content="text/html;charset=utf-8">
<title>{path} 的目录</title>
</head><body>
<h1>{path}的目录</h1><p></p>""").encode()
            # 获取当前路径下的各个文件、目录名
            subdirs=[] # 子目录名
            subfiles=[] # 子文件名
            for sub in os.listdir(path):
                # os.listdir()无法直接区分目录名和文件名, 因此还需进行判断
                if os.path.isfile(os.path.join(path,sub)): # 如果子项是文件
                    subfiles.append(sub)
                else: # 子项是目录
                    subdirs.append(sub)

            if dir != ".":
                response += f'\n<a href="/{dir}/..">[上级目录]</a><p></p>'.encode()
            # 依次显示各个子文件、目录
            for sub in subdirs:
                response += (f'\n<a href="/{dir}/{sub}">[目录]{sub}</a><p></p>').encode()
            for sub in subfiles:
                response += (f'\n<a href="/{dir}/{sub}">{sub}</a><p></p>').encode()
            response += b"\n</body></html>"
        else: # 不存在文件或目录
            # 若.html的后缀名省略，自动寻找html文件
            # 不过，例如要访问path，path/index.html要优先于path.html，用户可自行修改
            for ext in (".htm",".html"):
                file = path + ext
                if os.path.isfile(file):
                    with open(file,'rb') as f:
                        response = head + f.read()
                    return response
            raise OSError # 当做错误处理, 进入except语句

    except OSError:
        # 返回404
        response = head_404 + f"""
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

def handle_client(sock, address):# 处理客户端请求
    request_data = sock.recv(1024).decode()
    if request_data=="":return # 空数据
    #print(request_data)

    lines = request_data.splitlines()
    req_head = lines[0]
    req_info = {}
    for line in lines[1:]:
        lst = line.split(':', 1)
        try:
            key, value = lst[0].strip(), lst[1].strip()
            req_info[key] = value
        except (ValueError, IndexError):
            pass
    #print("请求数据:", req_head);pprint.pprint(req_info)

    if req_head.startswith("POST"): # POST请求
        data=parse_qs(lines[-1])
        if data == {}: # post含有多个tcp数据包时
            response=head_100 # 让客户端继续发送数据
        else:
            print("提交数据:",data)
            dir=parse_dir(req_head)
            response=head_ok + f"""
<html><head>
<meta http-equiv="content-type" content="text/html;charset=utf-8">
<title>提交成功</title>
</head><body>
<h1>提交成功</h1>
<a href="/{dir}">返回</a>
</body></html>
""".encode()
    else: # GET请求
        dir=parse_dir(req_head)
        print(address,"访问路径:",dir)
        response=getcontent(dir) # 构造响应数据

    # 向客户端返回响应数据
    sock.send(response)
    sock.close() # 关闭客户端连接

def _handle_client(*args,**kw): # 仅用于在多线程中handle_client产生异常时输出异常
    try:handle_client(*args,**kw)
    except Exception:
        traceback.print_exc()

PORT=80 # http的默认端口，选择80后在URL中可不加端口号。(也可改成其他端口)
if __name__ == "__main__":
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("", PORT))
    server_socket.listen(128)
    import webbrowser
    webbrowser.open('http://127.0.0.1:%d/'%PORT)

    # 单线程模式，一次处理一个客户端
    #while True:
    #    sock, address = server_socket.accept()
    #    handle_client(sock, address)
    # 多线程
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        while True:
            sock, address = server_socket.accept()
            #executor.submit(handle_client, client_socket)
            executor.submit(_handle_client, sock, address)
    client_socket.close()
