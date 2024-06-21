# http论坛程序, 主要基于post请求的处理

import socket,os,time,traceback,pprint
import json
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import parse_qs,unquote

FILENAME="database.json" # 数据库文件名
head_100=b"HTTP/1.1 100 Continue\n"
head_ok = b"HTTP/1.1 200 OK\n"
head_404 = b"HTTP/1.1 404 Not Found\n\n"
RECV_LENGTH = 16384 # sock.recv()一次接收内容的长度
data=[]
post_cache={} # 各个客户端的post请求提交数据的缓存，键为(IP,端口号)，值为已发送的内容(bytes类型)

def read_data():
    global data
    with open(FILENAME) as f:
        data=json.load(f)
def save_data():
    with open(FILENAME,"w") as f:
        json.dump(data,f)

def handle_client(sock, address):# 处理客户端请求
    raw = sock.recv(RECV_LENGTH)
    request_data = raw.decode()
    if request_data=="":return # 空数据

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
        completed=False
        content=raw.splitlines()[-1]
        
        length = int(req_info.get('Content-Length',-1))
        if len(content)<length: # 第一次调用sock.recv接收的内容不完整，就尝试继续接收数据
            while True:
                new_data = sock.recv(RECV_LENGTH)
                content += new_data
                if not new_data or len(content)>=length:break
            #content += sock.recv(length-len(content))
        if length != -1:content = content[:length] # 截断过长的数据
        # 用于处理多次POST请求（备用，一般不会遇到）
        key = (sock, address)
        if key not in post_cache:
            if len(content)>=length:
                completed=True
            else:post_cache[key] = content
        else:
            old = post_cache[key]
            content = old + content
            if len(content)>=length:
                completed=True
            else:post_cache[key] = content
        if completed:
            form=parse_qs(content.decode("utf-8"),encoding="utf-8")
            if "text" in form: # 如果用户输入了内容
                text = form["text"][0]
                print("新帖:",text)
                data.append(text)
                save_data()
            response=head_ok + b'''
<html><head>
<meta http-equiv="refresh" content="0;url=/"></head></html>''' # 提交完成后刷新页面
        else: # post含有多个tcp数据包且未完成
            response=head_100 # 让客户端继续发送数据

    else: # GET请求
        response=head_ok + """\n<html><head>
<meta http-equiv="content-type" content="text/html;charset=utf-8">
<title>简易论坛系统</title>
</head>

<body>
""".encode()
        for text in data:
            text_html=text.replace("\n","<br>")
            response+=b"<p>%s</p>\n" % text_html.encode()
        response+="""
<form id="form1" name="form1" method="post" action="">
  <p><textarea name="text" id="text" cols="45" rows="5"></textarea>
  </p>
  <input type="submit" name="button" id="button" value="发表" />
</form>
</body>
</html>
""".encode()

    # 向客户端返回响应数据
    sock.sendall(response)
    sock.close() # 关闭客户端连接

def _handle_client(*args,**kw): # 仅用于在多线程中handle_client产生异常时输出异常
    try:handle_client(*args,**kw)
    except Exception:
        traceback.print_exc()

PORT=80 # http的默认端口，选择80后在URL中可不加端口号。(也可改成其他端口)
if __name__ == "__main__":
    if os.path.isfile(FILENAME):
        read_data()
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
