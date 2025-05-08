# 改编自其他项目
import socket,traceback

CODING="utf-8"
# 设置IP和端口号
default_ip = "127.0.0.1" #socket.gethostbyname(socket.gethostname())
default_port=80
ip=input("输入IP地址 (默认 %s): "%default_ip).strip() or default_ip
port=int(input("输入端口号 (默认 %d): "%default_port).strip() or default_port)

addr = (ip, port)

# 创建套接字
sock = socket.socket()

# 连接服务器
sock.connect(addr)
print('已连接服务器 %s。'%str(addr))

try:
    while True:
        # 发送数据
        data = input('发送数据：')
        try:
            sock.send(data.encode(CODING))
            # 接收数据
            recv = sock.recv(16384)
        except ConnectionError as err:
            print("重新连接服务器 (%s): %s" % (type(err).__name__,str(err)))
            sock.close();sock = socket.socket()
            sock.connect(addr)
            sock.send(data.encode(CODING))
            recv = sock.recv(16384)
        print('接收数据：',recv.decode(CODING))

except BaseException:
    traceback.print_exc()

# 关闭套接字
sock.close()
print('断开服务器。')