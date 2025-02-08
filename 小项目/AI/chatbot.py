import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

# 简单的问答数据集
data = [
    ("你好", "你好！有什么可以帮您的吗？"),
    ("你叫什么名字", "我是一个简单的Chatbot。"),
    ("今天天气怎么样", "我不知道天气，但希望你有个好心情！"),
    ("再见", "再见！祝你一天愉快！")
]

# 构建词汇表
vocab = set()
for question, answer in data:
    vocab.update(question)
    vocab.update(answer)

vocab = {word: idx for idx, word in enumerate(vocab, start=1)}  # 单词到索引的映射
vocab["<PAD>"] = 0  # 填充符
vocab_size = len(vocab)

# 将句子转换为索引
def sentence_to_indices(sentence, vocab):
    return [vocab[word] for word in sentence]

data_indices = [
    (sentence_to_indices(question, vocab), sentence_to_indices(answer, vocab))
    for question, answer in data
]

# Scaled Dot-Product Attention
def scaled_dot_product_attention(query, key, value, mask=None):
    d_k = query.size(-1)  # 获取维度
    scores = torch.matmul(query, key.transpose(-2, -1)) / np.sqrt(d_k)  # 点积注意力
    if mask is not None:
        scores = scores.masked_fill(mask == 0, -1e9)  # 应用掩码
    attention_weights = torch.softmax(scores, dim=-1)  # 归一化
    return torch.matmul(attention_weights, value), attention_weights

# Multi-Head Attention
class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, num_heads):
        super(MultiHeadAttention, self).__init__()
        self.num_heads = num_heads
        self.d_model = d_model

        assert d_model % num_heads == 0  # 确保可以均分

        self.depth = d_model // num_heads
        self.wq = nn.Linear(d_model, d_model)
        self.wk = nn.Linear(d_model, d_model)
        self.wv = nn.Linear(d_model, d_model)
        self.dense = nn.Linear(d_model, d_model)

    def split_heads(self, x, batch_size):
        x = x.view(batch_size, -1, self.num_heads, self.depth)
        return x.permute(0, 2, 1, 3)  # (batch_size, num_heads, seq_len, depth)

    def forward(self, query, key, value, mask):
        batch_size = query.size(0)

        query = self.split_heads(self.wq(query), batch_size)
        key = self.split_heads(self.wk(key), batch_size)
        value = self.split_heads(self.wv(value), batch_size)

        attention, _ = scaled_dot_product_attention(query, key, value, mask)
        attention = attention.permute(0, 2, 1, 3).contiguous()  # (batch_size, seq_len, num_heads, depth)
        attention = attention.view(batch_size, -1, self.d_model)  # 合并头
        return self.dense(attention)

# 位置编码
class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=5000):
        super(PositionalEncoding, self).__init__()
        self.encoding = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2) * -(np.log(10000.0) / d_model))
        self.encoding[:, 0::2] = torch.sin(position * div_term)
        self.encoding[:, 1::2] = torch.cos(position * div_term)
        self.encoding = self.encoding.unsqueeze(0)

    def forward(self, x):
        seq_len = x.size(1)
        return x + self.encoding[:, :seq_len, :].to(x.device)

# 前馈网络
class FeedForward(nn.Module):
    def __init__(self, d_model, d_ff, dropout=0.1):
        super(FeedForward, self).__init__()
        self.linear1 = nn.Linear(d_model, d_ff)
        self.dropout = nn.Dropout(dropout)
        self.linear2 = nn.Linear(d_ff, d_model)

    def forward(self, x):
        return self.linear2(self.dropout(torch.relu(self.linear1(x))))

# 编码器层
class EncoderLayer(nn.Module):
    def __init__(self, d_model, num_heads, d_ff, dropout=0.1):
        super(EncoderLayer, self).__init__()
        self.mha = MultiHeadAttention(d_model, num_heads)
        self.ffn = FeedForward(d_model, d_ff, dropout)
        self.layernorm1 = nn.LayerNorm(d_model)
        self.layernorm2 = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x, mask):
        attn_output = self.mha(x, x, x, mask)
        out1 = self.layernorm1(x + self.dropout(attn_output))
        ffn_output = self.ffn(out1)
        return self.layernorm2(out1 + self.dropout(ffn_output))

# 解码器层
class DecoderLayer(nn.Module):
    def __init__(self, d_model, num_heads, d_ff, dropout=0.1):
        super(DecoderLayer, self).__init__()
        self.mha1 = MultiHeadAttention(d_model, num_heads)
        self.mha2 = MultiHeadAttention(d_model, num_heads)
        self.ffn = FeedForward(d_model, d_ff, dropout)
        self.layernorm1 = nn.LayerNorm(d_model)
        self.layernorm2 = nn.LayerNorm(d_model)
        self.layernorm3 = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x, enc_output, look_ahead_mask, padding_mask):
        attn1 = self.mha1(x, x, x, look_ahead_mask)
        out1 = self.layernorm1(x + self.dropout(attn1))

        attn2 = self.mha2(out1, enc_output, enc_output, padding_mask)
        out2 = self.layernorm2(out1 + self.dropout(attn2))

        ffn_output = self.ffn(out2)
        return self.layernorm3(out2 + self.dropout(ffn_output))

# Transformer 模型
class Transformer(nn.Module):
    def __init__(self, num_layers, d_model, num_heads, d_ff, input_vocab_size, target_vocab_size, max_seq_length, dropout=0.1):
        super(Transformer, self).__init__()
        self.encoder = nn.ModuleList([EncoderLayer(d_model, num_heads, d_ff, dropout) for _ in range(num_layers)])
        self.decoder = nn.ModuleList([DecoderLayer(d_model, num_heads, d_ff, dropout) for _ in range(num_layers)])
        self.pos_encoding = PositionalEncoding(d_model, max_seq_length)
        self.final_layer = nn.Linear(d_model, target_vocab_size)

    def encode(self, x, mask):
        for layer in self.encoder:
            x = layer(x, mask)
        return x

    def decode(self, x, enc_output, look_ahead_mask, padding_mask):
        for layer in self.decoder:
            x = layer(x, enc_output, look_ahead_mask, padding_mask)
        return x

    def forward(self, enc_input, dec_input, enc_mask, dec_mask):
        enc_output = self.encode(self.pos_encoding(enc_input), enc_mask)
        dec_output = self.decode(self.pos_encoding(dec_input), enc_output, dec_mask, enc_mask)
        return self.final_layer(dec_output)

# 训练模型
def train_model(model, data_indices, num_epochs=100, learning_rate=0.001):
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    criterion = nn.CrossEntropyLoss(ignore_index=0)  # 忽略填充符的损失

    for epoch in range(num_epochs):
        for question_indices, answer_indices in data_indices:
            # 准备输入
            enc_input = torch.tensor(question_indices).unsqueeze(0)  # (1, seq_len)
            dec_input = torch.tensor(answer_indices).unsqueeze(0)  # (1, seq_len)

            # 创建掩码
            enc_mask = None  # 这里可以实现掩码
            dec_mask = None  # 这里可以实现掩码

            # 前向传播
            optimizer.zero_grad()
            output = model(enc_input, dec_input, enc_mask, dec_mask)

            # 计算损失
            loss = criterion(output.view(-1, vocab_size), dec_input.view(-1))
            loss.backward()
            optimizer.step()

        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch + 1}, Loss: {loss.item():.4f}")

# 测试模型
def test_model(model, question):
    model.eval()
    question_indices = sentence_to_indices(question, vocab)
    enc_input = torch.tensor(question_indices).unsqueeze(0)  # (1, seq_len)
    dec_input = torch.zeros((1, 1), dtype=torch.long)  # (1, 1) 开始符

    # 创建掩码
    enc_mask = None  # 这里可以实现掩码
    dec_mask = None  # 这里可以实现掩码

    # 生成回复
    for _ in range(10):  # 限制回复长度
        output = model(enc_input, dec_input, enc_mask, dec_mask)
        next_word = output[:, -1, :].argmax(dim=-1).item()  # 选择下一个单词
        dec_input = torch.cat([dec_input, torch.tensor([[next_word]])], dim=1)  # 添加到输入中

        if next_word == vocab["<PAD>"]:  # 如果生成填充符，停止生成
            break

    response = ''.join([list(vocab.keys())[list(vocab.values()).index(idx)] for idx in dec_input[0].tolist() if idx != 0])
    return response

# 设置超参数
num_layers = 2
d_model = 64
num_heads = 4
d_ff = 128
max_seq_length = 10

# 创建 Transformer 模型
model = Transformer(num_layers, d_model, num_heads, d_ff, vocab_size, vocab_size, max_seq_length)

# 训练模型
train_model(model, data_indices, num_epochs=100)

# 测试模型
user_input = "你好"
response = test_model(model, user_input)
print(f"Chatbot: {response}")

