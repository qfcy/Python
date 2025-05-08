import random

# 定义环境
R = [[-1, -1, -1, -1, 0, -1],
     [-1, -1, -1, 0, -1, 100],
     [-1, -1, -1, 0, -1, -1],
     [-1, 0, 0, -1, 0, -1],
     [0, -1, -1, 0, -1, 100],
     [-1, 0, -1, -1, 0, 100]]

# 初始化 Q 表
Q = [[0 for _ in range(6)] for _ in range(6)]

# 定义参数
gamma = 0.8
alpha = 0.1
num_episodes = 1000

# Q-learning 算法
for _ in range(num_episodes):
    state = random.randint(0, 5)
    while True:
        # 获取当前状态下可选的动作
        possible_actions = [i for i in range(6) if R[state][i] >= 0]
        # 随机选择一个动作
        action = random.choice(possible_actions)
        next_state = action
        # 获取下一个状态下可选的动作
        next_possible_actions = [i for i in range(6) if R[next_state][i] >= 0]
        # 更新 Q 表
        Q[state][action] += alpha * (R[state][action] + gamma * max([Q[next_state][a] for a in next_possible_actions]) - Q[state][action])
        state = next_state
        if state == 5:
            break

print("Q-table:")
for row in Q:
    print(row)

# 测试
state = 2;actions = 0
while state != 5 and actions < 20:
    print("当前状态:", state)
    # 选择具有最大 Q 值的动作
    action = max(enumerate(Q[state]), key=lambda x: x[1])[0]
    print("采取的动作:", action)
    state = action
    actions += 1
if state == 5:
    print("到达终点！")
else:
    print("测试失败！")