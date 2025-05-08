import socket

# 创建UDP服务器
address = ('127.0.0.1', 8001)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(address)  # 绑定IP和端口

print("服务器正在于%s运行，等待接收消息..."%str(address))
while True:
    data, addr = server_socket.recvfrom(1024)  # 接收数据报
    print(f"接收到来自{addr}的消息: {data.decode()}")