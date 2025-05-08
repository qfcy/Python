import numpy as np

class SimpleTransformer:
    def __init__(self, input_dim, model_dim, num_heads, num_tokens):
        self.input_dim = input_dim
        self.model_dim = model_dim
        self.num_heads = num_heads
        self.num_tokens = num_tokens

        # 初始化权重
        self.Wq = np.random.rand(input_dim, model_dim) * 0.01
        self.Wk = np.random.rand(input_dim, model_dim) * 0.01
        self.Wv = np.random.rand(input_dim, model_dim) * 0.01
        self.Wo = np.random.rand(model_dim * num_heads, input_dim) * 0.01
        self.Wf = np.random.rand(input_dim, input_dim) * 0.01

        # 偏置项
        self.bf = np.zeros((1, input_dim))

    def attention(self, Q, K, V):
        # 计算注意力分数
        scores = np.dot(Q, K.T) / np.sqrt(self.model_dim)
        weights = self.softmax(scores)
        output = np.dot(weights, V)
        return output, weights

    def softmax(self, x):
        exp_x = np.exp(x - np.max(x, axis=-1, keepdims=True))
        return exp_x / np.sum(exp_x, axis=-1, keepdims=True)

    def forward(self, x):
        # 输入 x 的形状为 (num_tokens, input_dim)
        Q = np.dot(x, self.Wq)
        K = np.dot(x, self.Wk)
        V = np.dot(x, self.Wv)

        # 计算多头注意力
        head_outputs = []
        for i in range(self.num_heads):
            head_output, _ = self.attention(Q, K, V)
            head_outputs.append(head_output)

        # 拼接头输出
        multi_head_output = np.concatenate(head_outputs, axis=-1)
        output = np.dot(multi_head_output, self.Wo)

        # 前馈网络
        output = np.maximum(0, np.dot(output, self.Wf) + self.bf)  # ReLU 激活
        return output

    def backward(self, x, grad_output, learning_rate):
        # 简单实现：仅更新前馈网络的权重
        grad_Wf = np.dot(x.T, grad_output)
        grad_bf = np.sum(grad_output, axis=0, keepdims=True)

        # 更新权重
        self.Wf -= learning_rate * grad_Wf
        self.bf -= learning_rate * grad_bf


# 数据生成函数
def generate_data(num_samples, input_dim, output_dim):
    X = np.random.rand(num_samples, input_dim)
    Y = np.dot(X, np.random.rand(input_dim, output_dim))  # 简单线性映射
    return X, Y

# 损失函数
def mse_loss(y_pred, y_true):
    return np.mean((y_pred - y_true) ** 2)

# 损失的梯度
def mse_loss_grad(y_pred, y_true):
    return 2 * (y_pred - y_true) / y_true.size

# 训练函数
def train(transformer, X_train, Y_train, epochs, learning_rate):
    for epoch in range(epochs):
        # 前向传播
        y_pred = transformer.forward(X_train)

        # 计算损失
        loss = mse_loss(y_pred, Y_train)

        # 反向传播
        grad_loss = mse_loss_grad(y_pred, Y_train)
        transformer.backward(X_train, grad_loss, learning_rate)

        # 打印损失
        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch + 1}/{epochs}, Loss: {loss:.4f}")

# 测试函数
def test(transformer, X_test, Y_test):
    y_pred = transformer.forward(X_test)
    loss = mse_loss(y_pred, Y_test)
    print(f"Test Loss: {loss:.4f}")
    return y_pred


# 参数设置
input_dim = 64   # 输入维度
model_dim = 32   # 模型维度
num_heads = 4    # 注意力头数
num_tokens = 20  # token 数量
output_dim = 64  # 输出维度
learning_rate = 0.01
epochs = 2000

# 创建 Transformer
transformer = SimpleTransformer(input_dim, model_dim, num_heads, num_tokens)

# 生成训练和测试数据
X_train, Y_train = generate_data(100, input_dim, output_dim)
print("X_train:",list(X_train),"\nY_train:",list(Y_train))
X_test, Y_test = generate_data(20, input_dim, output_dim)
print("X_test:",list(X_test),"\nY_test:",list(Y_test))

# 训练模型
train(transformer, X_train, Y_train, epochs, learning_rate)

# 测试模型
test(transformer, X_test, Y_test)