import socket

# 创建套接字
tcpServerSocket = socket.socket()

# 设置IP和端口号
ip = socket.gethostbyname(socket.gethostname())
tcpServerAddress = (ip,7788)

# 绑定IP和端口号
tcpServerSocket.bind(tcpServerAddress)

# 打开监听
tcpServerSocket.listen(6)
print('打开监听，等待客户端连接。')

# 等待客户端连接
tcpClientSocket, tcpClientAddress = tcpServerSocket.accept()
print('客户端已连接：',tcpClientAddress)

while 1:
    # 接收数据
    tcpServerReceiveData = tcpClientSocket.recv(1024)  
    print('接收客户端数据：',tcpServerReceiveData.decode("gbk"))

    if tcpServerReceiveData.decode("gbk") == '断开连接':
        break

    # 发送数据
    tcpServerSendData = input('发送客户端数据：')
    tcpClientSocket.send(tcpServerSendData.encode("gbk")) 

# 关闭套接字
tcpClientSocket.close()
tcpServerSocket.close()
print('关闭服务器。')