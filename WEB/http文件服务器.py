import socket, os, time
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import unquote

# http响应头
head = b"""HTTP/1.1 200 OK\n\n"""
head_404 = b"""HTTP/1.1 404 Not Found\n\n"""

def handle_client(client_socket):
    # 处理客户端请求
    request_data = client_socket.recv(1024).decode()
    req = {}
    lines = request_data.splitlines()
    req_head = lines[0]
    for line in lines:
        lst = line.split(':', 1)
        try:
            key, value = lst[0].strip(), lst[1].strip()
            req[key] = value
        except (ValueError, IndexError):
            pass
    #print("请求数据:", req)

    dir = unquote(req_head.split(' ')[1])[1:] # 请求的url后面的路径, 在请求数据的第一行
    if dir == "":
        dir="."
    if dir[-1] in ("/","\\"):
        dir=dir[:-1]
    # 获取url对应的文件路径
    path = os.path.join(os.getcwd(),dir)
    print("访问路径:", path)
    # 构造响应数据
    try:
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
            # os.listdir()无法直接区分目录名和文件名, 因此还需进行判断
            for sub in os.listdir(path):
                if os.path.isfile(os.path.join(path,sub)): # 如果子项是文件
                    subfiles.append(sub)
                else: # 子项是目录
                    subdirs.append(sub)

            if dir != ".":
                response += f'<a href="/{dir}/..">[上级目录]</a><p></p>'.encode()
            # 依次显示各个子文件、目录
            for sub in subdirs:
                response += (f'<a href="/{dir}/{sub}">[目录]{sub}</a><p></p>').encode()
            for sub in subfiles:
                response += (f'<a href="/{dir}/{sub}">{sub}</a><p></p>').encode()
            response += b"</body></html>"
        else: # 没有找到文件或目录
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

    # 向客户端返回响应数据
    client_socket.send(response)
    # 关闭客户端连接
    client_socket.close()


if __name__ == "__main__":
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("", 8000))
    server_socket.listen(128)
    import webbrowser
    webbrowser.open('http://127.0.0.1:8000/')
    # 以下用于调试, 因为多线程中看不到错误消息
    #while True:
    #    client_socket, client_address = server_socket.accept()
    #    handle_client(client_socket)
    # 多线程
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        while True:
            client_socket, client_address = server_socket.accept()
            #print("[%s, %s]用户连接上了" % client_address)
            executor.submit(handle_client, client_socket)
    client_socket.close()
