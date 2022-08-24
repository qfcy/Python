import socket

# 创建套接字
tcpClientSocket = socket.socket()

# 设置IP和端口号
ip = socket.gethostbyname(socket.gethostname())
tcpServerAddress = (ip,7788)

# 连接服务器
tcpClientSocket.connect(tcpServerAddress)
print('服务器已连接。')

while 1:

    # 发送数据
    tcpClientSendData = input('发送服务器数据：')
    tcpClientSocket.send(tcpClientSendData.encode("gbk"))

    if tcpClientSendData == '断开连接':
        break

    # 接收数据
    tcpClientReceiveData = tcpClientSocket.recv(1024)  
    print('接收服务器数据：',tcpClientReceiveData.decode("gbk"))

# 关闭套接字
tcpClientSocket.close()
print('断开服务器。')