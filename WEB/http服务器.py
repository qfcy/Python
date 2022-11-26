import socket,os,time
from concurrent.futures import ThreadPoolExecutor

def handle_client(client_socket):
    # 处理客户端请求
    request_data = client_socket.recv(1024)
    print("请求数据:", request_data.decode())
    # 构造响应数据
    response_start_line = "HTTP/1.1 200 OK\r\n"
    response_headers = "Server: PyServer\r\n"
    response_body = """<html><head>
<meta http-equiv="content-type" content="text/html;charset=utf-8">
</head>
<body><h1>Python HTTP Test</h1>"""
    if b"Trident" in request_data: # 识别浏览器类型
        response_body += "<p>IE 浏览器</p>"
    response_body += "</body></html>"
    response = response_start_line + response_headers + "\r\n" + response_body

    # 向客户端返回响应数据
    client_socket.send(bytes(response, "utf-8"))

    # 关闭客户端连接
    client_socket.close()


if __name__ == "__main__":
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("", 8000))
    server_socket.listen(128)
    import webbrowser
    webbrowser.open('http://127.0.0.1:8000/')
    # 多线程
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        while True:
            client_socket, client_address = server_socket.accept()
            print("[%s, %s]用户连接上了" % client_address)
            executor.submit(handle_client, client_socket)
    client_socket.close()