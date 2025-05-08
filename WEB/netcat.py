# 类似netcat命令行的工具（备用）
import sys,socket,ast,time

def main():
    if len(sys.argv) != 3:
        print(f"用法: python {sys.argv[0]} host port")
        return

    host = sys.argv[1]
    port = int(sys.argv[2])

    try:
        sock = socket.create_connection((host, port))
        sock.setblocking(False)
        print(f"已连接到 {host}:{port}")
    except Exception as e:
        print(f"连接失败: {e}")
        return

    try:
        while True:
            # 接收数据
            while True:
                try:
                    data = sock.recv(4096)
                    break
                except BlockingIOError:
                    print(".",end="",flush=True)
                    time.sleep(0.5)
                except Exception as err:
                    print(f"{type(err).__name__}: {err}")
                    break
            # 显示 bytes 的转义字符串
            print("收到:", repr(data))

            # 用户输入处理，例如输入 b'abc\x01'
            s = input("输入要发送的数据（如 b'\\x01'）：").strip()
            if not s:
                continue
            try:
                to_send = ast.literal_eval(s)
                sock.sendall(to_send)
            except Exception as err:
                print(f"{type(err).__name__}: {err}")
    finally:
        sock.close()

if __name__ == "__main__":
    main()