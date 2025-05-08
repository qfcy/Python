import builtins,random

def input(prompt=None):
    # 重写input函数
    while True:
        result=builtins.input(prompt)
        if result.strip():return result

class Nim:
    PILES=3
    MIN=3;MAX=30
    def __init__(self,min_=MIN,max_=MAX,piles=PILES):
        self.piles = [random.randint(min_, max_+1) for _ in range(piles)]

    def nim_sum(self):
        """计算当前局面的 Nim 和"""
        nim_sum = 0
        for pile in self.piles:
            nim_sum ^= pile
        return nim_sum

    def player_move(self, pile_index, stones):
        """处理玩家的移动"""
        if 0 <= pile_index < len(self.piles) and 0 < stones <= self.piles[pile_index]:
            self.piles[pile_index] -= stones
            return True
        return False

    def computer_move(self):
        """计算机的操作（最佳策略）"""
        nim_sum = self.nim_sum()
        if nim_sum == 0:
            # 如果当前局面是必败态，随机选择一个堆取石子
            while True:
                pile_index = random.randint(0, len(self.piles) - 1)
                if self.piles[pile_index] > 0:
                    stones = random.randint(1, self.piles[pile_index])
                    #stones = 1 # 贪心版本，延长对手获胜需要的时间
                    self.piles[pile_index] -= stones
                    return pile_index, stones
        else:
            # 如果当前局面是必胜态，找到最佳操作
            for i in range(len(self.piles)):
                if self.piles[i] ^ nim_sum < self.piles[i]:
                    stones = self.piles[i] - (self.piles[i] ^ nim_sum)
                    self.piles[i] -= stones
                    return i, stones
        return None, None

    def is_game_over(self):
        """判断游戏是否结束"""
        return all(pile == 0 for pile in self.piles)


class NimController:
    def __init__(self):
        self.reset()
    def reset(self):
        self.game = Nim()

    def play_human_vs_computer(self):
        """人机对弈"""
        print("欢迎来到 Nim 游戏！")
        while True:
            # 玩家回合
            print("\n玩家回合：")
            print(f"当前石子堆：{self.game.piles} Nim和：{self.game.nim_sum()}")
            pile_index = int(input(f"请选择要取石子的堆 (0-{len(self.game.piles) - 1}): "))
            if not 0<=pile_index<len(self.game.piles):
                print("无效的索引，请重新输入");continue
            stones = int(input(f"从第 {pile_index} 堆中取走的石子数量 (1-{self.game.piles[pile_index]}): "))
            if self.game.player_move(pile_index, stones):
                if self.game.is_game_over():
                    print("恭喜你获胜了！")
                    break

                print(f"当前石子堆：{self.game.piles} Nim和：{self.game.nim_sum()}")
                # 计算机回合
                print("\n计算机回合：")
                pile_index, stones = self.game.computer_move()
                print(f"计算机从第 {pile_index} 堆中取走了 {stones} 个石子。")
                if self.game.is_game_over():
                    print("计算机获胜了！")
                    break
            else:
                print("无效的移动，请重新输入。")
    def play_computer_vs_computer(self):
        """两个计算机对弈"""
        print("欢迎来到 Nim 游戏！这是两个计算机之间的对弈。")
        print(f"初始石子堆：{self.game.piles} Nim和：{self.game.nim_sum()}")
        turn = 0
        while True:
            print(f"\n轮到计算机 {turn + 1}：")
            pile_index, stones = self.game.computer_move()
            print(f"计算机 {turn + 1} 从第 {pile_index} 堆中取走了 {stones} 个石子。")
            print(f"当前石子堆：{self.game.piles} Nim和：{self.game.nim_sum()}")
            if self.game.is_game_over():
                print(f"计算机 {turn + 1} 获胜！")
                break
            turn = (turn+1) % 2  # 切换回合
    def play_human_vs_human(self):
        """两人对弈"""
        print("欢迎来到 Nim 游戏！这是两个玩家之间的对弈。")
        print(f"初始石子堆：{self.game.piles} Nim和：{self.game.nim_sum()}")
        turn = 0
        while True:
            print(f"\n轮到玩家 {turn + 1}：")
            print(f"当前石子堆：{self.game.piles} Nim和：{self.game.nim_sum()}")
            pile_index = int(input(f"请选择要取石子的堆 (0-{len(self.game.piles) - 1}): "))
            if not 0<=pile_index<len(self.game.piles):
                print("无效的索引，请重新输入");continue
            stones = int(input(f"从第 {pile_index} 堆中取走的石子数量 (1-{self.game.piles[pile_index]}): "))
            if self.game.player_move(pile_index, stones):
                if self.game.is_game_over():
                    print(f"玩家 {turn + 1} 获胜！")
                    break
                turn = (turn + 1) % 2  # 切换回合
            else:
                print("无效的移动，请重新输入。")

def main():
    """主菜单"""
    controller = NimController()
    while True:
        print("\n欢迎来到 Nim 游戏！请选择模式：")
        print("1. 人机对弈")
        print("2. 两个计算机对弈")
        print("3. 两人对弈")
        print("4. 自定义石子堆")
        print("0. 退出游戏")
        try:
            choice = int(input("请输入你的选择 (0~4): "))
            if not 0<=choice<=4:raise ValueError
        except Exception:
            print("无效的选择，请重新输入。")
            continue

        if choice == 1:
            try:controller.play_human_vs_computer()
            except KeyboardInterrupt:
                print("\n玩家已中途退出\n")
        elif choice == 2:
            controller.play_computer_vs_computer()
        elif choice == 3:
            try:controller.play_human_vs_human()
            except KeyboardInterrupt:
                print("\n玩家已中途退出\n")
        elif choice == 4:
            try:
                controller.game.piles=[
                    int(num) for num in input("输入石子堆 (如: 1 2 3): ").split()]
            except Exception as err:
                print("无效输入，请重试 (%s): %s"%(type(err).__name__,str(err)))
        elif choice == 0:
            print("感谢你的游玩，再见！")
            break

        if choice != 4:
            controller.reset() # 重置石子堆

if __name__ == "__main__":
    main()
