# 来自于AI生成的代码，并加以修改
class MersenneTwister:
    def __init__(self, seed):
        # seed的范围为-2147483648到2147483647
        self.index = 624  # 初始化索引
        self.mt = [0] * 624  # 初始化状态数组
        self.mt[0] = seed  # 使用种子初始化状态数组的第一个元素
        for i in range(1, 624):  # 初始化状态数组的其余元素
            self.mt[i] = 0xFFFFFFFF & (1812433253 * (self.mt[i - 1] ^ (self.mt[i - 1] >> 30)) + i)

    def extract_number(self):
        if self.index >= 624:  # 如果索引超出范围，进行扭曲操作
            self.twist()

        y = self.mt[self.index]  # 取出状态数组中的一个元素
        y = y ^ (y >> 11)  # 对取出的元素进行位运算
        y = y ^ ((y << 7) & 0x9D2C5680)  # 对取出的元素进行位运算
        y = y ^ ((y << 15) & 0xEFC60000)  # 对取出的元素进行位运算
        y = y ^ (y >> 18)  # 对取出的元素进行位运算

        self.index += 1  # 更新索引
        return 0xFFFFFFFF & y  # 返回生成的随机数
    def random(self):
        # 返回0-1的随机数
        return self.extract_number() / 0xFFFFFFFF

    def twist(self):
        for i in range(624):  # 扭曲操作
            y = (self.mt[i] & 0x80000000) + (self.mt[(i + 1) % 624] & 0x7fffffff)
            self.mt[i] = self.mt[(i + 397) % 624] ^ (y >> 1)
            if y % 2 != 0:
                self.mt[i] = self.mt[i] ^ 0x9908B0DF
        self.index = 0  # 重置索引

def main():
    seed = 5489  # 设置随机数种子
    mt = MersenneTwister(seed)
    print("按Enter生成随机数，按Ctrl+C退出 ...")
    while True:
        print(mt.random(),end="")  # 生成0-1的随机数
        input() # 等待用户按下回车键
        

if __name__ == "__main__":
    main()
