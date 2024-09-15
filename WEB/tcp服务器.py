# 本文件改编自其他项目
import socket

CODING="utf-8"
# 创建套接字
sock = socket.socket()

# 设置IP和端口号
ip = "127.0.0.1" #socket.gethostbyname(socket.gethostname())
server_addr = (ip,8000)

# 绑定IP和端口号
sock.bind(server_addr)

# 打开监听
sock.listen(128)
print('在%s打开监听，等待客户端连接。'%str(server_addr))

# 等待客户端连接
client_sock, address = sock.accept()
print('客户端已连接：',address)

while True:
    # 接收数据
    recv = client_sock.recv(1024)
    print('接收客户端数据：',recv.decode(CODING))

    # 发送数据
    data = input('发送客户端数据：')
    client_sock.send(data.encode(CODING))

# 关闭套接字
client_sock.close()
sock.close()
print('关闭服务器。')