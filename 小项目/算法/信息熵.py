import sys,os,math
from collections import Counter

def calc_entropy(data):
    # 计算字节频率
    byte_counter = Counter(data)
    total_bytes = len(data)

    # 计算熵
    entropy = 0
    for count in byte_counter.values():
        probability = count / total_bytes
        entropy -= probability * math.log2(probability)

    return entropy

def main():
    files = sys.argv[1:]

    if not files:
        print("用法：python %s <文件1> <文件2> ...  "%sys.argv[0])
        return

    for path in files:
        if os.path.isfile(path):
            with open(path, 'rb') as f:
                data = f.read()
            entropy = calc_entropy(data)
            print(f"文件 '{path}' 的信息熵为：{entropy:.6f} b")
        else:
            print(f"路径 '{path}' 不是有效的文件！")

if __name__ == "__main__":main()
