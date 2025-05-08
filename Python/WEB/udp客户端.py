import socket

# 创建UDP客户端
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('localhost', 8001)

try:
    while True:
        # 发送数据
        data = input('发送数据：')
        client_socket.sendto(data.encode(), server_address)  # 发送数据
finally:
    client_socket.close()  # 关闭客户端