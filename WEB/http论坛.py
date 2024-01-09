# http论坛程序, 主要基于post请求的处理

import socket, os, time,traceback,pprint
import json
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import parse_qs,unquote

FILENAME="database.json" # 数据库文件名
head_100=b"HTTP/1.1 100 Continue\n"
head_ok = b"HTTP/1.1 200 OK\n"
head_404 = b"HTTP/1.1 404 Not Found\n\n"
data=[]

def read_data():
    global data
    with open(FILENAME) as f:
        data=json.load(f)
def save_data():
    with open(FILENAME,"w") as f:
        json.dump(data,f)

def handle_client(sock, address):# 处理客户端请求
    request_data = sock.recv(16384).decode()
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
        form=parse_qs(lines[-1],encoding="utf-8")
        if form != {}:
            if "text" in form: # 如果用户输入了内容
                text = form["text"][0]
                print("新帖:",text)
                data.append(text)
                save_data()
            response=head_ok + b'''
<html><head>
<meta http-equiv="refresh" content="0;url=/"></head></html>'''
        else: # post含有多个tcp数据包时
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
