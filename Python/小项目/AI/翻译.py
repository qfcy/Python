import torch  
import torch.nn as nn  
import torch.optim as optim  
from torch.utils.data import Dataset, DataLoader  
import jieba

# 定义超参数  
BATCH_SIZE = 2  
LEARNING_RATE = 0.001  
EPOCHS = 30
MAX_LEN = 10  # 最大句子长度  
D_MODEL = 64  # 嵌入维度  
NHEAD = 2  # 注意力头数  
NUM_ENCODER_LAYERS = 2  # 编码器层数  
NUM_DECODER_LAYERS = 2  # 解码器层数  

# 定义数据集类  
class TranslationDataset(Dataset):  
    def __init__(self, data):  
        self.data = data  

    def __len__(self):  
        return len(self.data)  

    def __getitem__(self, idx):  
        src, tgt = self.data[idx]  
        return torch.tensor(src, dtype=torch.long), torch.tensor(tgt, dtype=torch.long)  

# 定义Transformer模型  
class SimpleTransformer(nn.Module):  
    def __init__(self, vocab_size, d_model, nhead):  
        super(SimpleTransformer, self).__init__()  
        self.embedding = nn.Embedding(vocab_size, d_model)  
        self.transformer = nn.Transformer(  
            d_model=d_model,  
            nhead=nhead,  
            num_encoder_layers=NUM_ENCODER_LAYERS,  
            num_decoder_layers=NUM_DECODER_LAYERS,  
        )  
        self.fc_out = nn.Linear(d_model, vocab_size)  

    def forward(self, src, tgt):  
        src = self.embedding(src)  # (seq_len, batch_size, d_model)  
        tgt = self.embedding(tgt)  # (seq_len, batch_size, d_model)  
        out = self.transformer(src, tgt)  # (seq_len, batch_size, d_model)  
        return self.fc_out(out)  # (seq_len, batch_size, vocab_size)  

# 准备训练数据
vocab = [  
    ("I", "我"),
    ("this", "这"),  
    ("is", "是"),  
    ("her", "她的"),  
    ("hat", "帽子"),  
    ("he", "他"),  
    ("like", "喜欢"),  
    ("likes", "喜欢"),  
    ("to", "去"),  
    ("play", "玩"),  
    ("football", "足球"),  
    ("and", "和"),  
    ("basketball", "篮球"),  
    ("he","他"),
    ("she", "她"),  
    ("read", "阅读"),  
    ("book", "书籍"),  
    ("reads", "阅读"),  
    ("books", "书籍"),  
    ("every", "每"),  
    ("day", "天"),  
    ("we", "我们"),  
    ("go", "去"),  
    ("to", "到"),  
    ("school", "学校"),  
    ("together", "一起"),  
    ("they", "他们"),  
    ("eat", "吃"),  
    ("lunch", "午餐"),  
    ("at", "在"),  
    ("noon", "中午"),  
    ("my", "我的"),  
    ("favorite", "最喜欢的"),  
    ("color", "颜色"),  
    ("is", "是"),  
    ("blue", "蓝色"),  
    ("green", "绿色"),  
    ("red", "红色"),  
    ("yellow", "黄色"),  
    ("orange", "橙色"),  
    ("purple", "紫色"),  
    ("brown", "棕色"),  
    ("black", "黑色"),  
    ("white", "白色"),  
    ("cat", "猫"),  
    ("dog", "狗"),  
    ("fish", "鱼"),  
    ("bird", "鸟"),  
    ("rabbit", "兔子"),  
    ("horse", "马"),  
]
vocab=[(eng,chs) for eng,chs in vocab]
train_data = [  
    ("I am a student", "我是一个学生"),  
    ("He is a teacher", "他是一个老师"),  
    ("She is a doctor", "她是一个医生"),  
    ("We are friends", "我们是朋友"),  
    ("They are happy", "他们很高兴"),  
    ("This is a book", "这是一本书"),  
    ("That is a pen", "那是一支笔"),  
    ("I like apples", "我喜欢苹果"),  
    ("He likes bananas", "他喜欢香蕉"),  
    ("She likes oranges", "她喜欢橙子"),  
    ("We like reading", "我们喜欢阅读"),  
    ("They like playing", "他们喜欢玩耍"),  
    ("I have a dog", "我有一只狗"),  
    ("He has a cat", "他有一只猫"),  
    ("She has a bird", "她有一只鸟"),  
    ("We have a car", "我们有一辆车"),  
    ("They have a house", "他们有一栋房子"),  
    ("I can swim", "我会游泳"),  
    ("He can run", "他会跑步"),  
    ("She can sing", "她会唱歌"),  
    ("We can dance", "我们会跳舞"),  
    ("They can jump", "他们会跳"),  
    ("I want to eat", "我想吃东西"),  
    ("He wants to drink", "他想喝水"),  
    ("She wants to sleep", "她想睡觉"),  
    ("We want to play", "我们想玩"),  
    ("They want to study", "他们想学习"),  
    ("I am happy", "我很高兴"),  
    ("He is sad", "他很伤心"),  
    ("She is angry", "她很生气"),  
    ("We are tired", "我们很累"),  
    ("They are excited", "他们很兴奋"),  
    ("This is my bag", "这是我的书包"),  
    ("That is his hat", "那是他的帽子"),  
    ("This is her dress", "这是她的裙子"),  
    ("These are our shoes", "这些是我们的鞋子"),  
    ("Those are their toys", "那些是他们的玩具"),  
    ("I love my family", "我爱我的家人"),  
    ("He loves his mother", "他爱他的妈妈"),  
    ("She loves her father", "她爱她的爸爸"),  
    ("We love our teacher", "我们爱我们的老师"),  
    ("They love their school", "他们爱他们的学校"),  
    ("I see a bird", "我看到一只鸟"),  
    ("He sees a plane", "他看到一架飞机"),  
    ("She sees a car", "她看到一辆车"),  
    ("We see a tree", "我们看到一棵树"),  
    ("They see a flower", "他们看到一朵花"),  
    ("I hear a sound", "我听到一个声音"),  
    ("He hears music", "他听到音乐"),  
    ("She hears a baby", "她听到一个婴儿"),  
    ("We hear the wind", "我们听到风声"),  
    ("They hear the rain", "他们听到雨声"),  
]
#train_data.extend(vocab)
cut_data = []
for eng,chn in train_data:
    cut_data.append((tuple(word.lower() for word in eng.split()),tuple(jieba.cut(chn))))
print(cut_data)
# 构建词汇表  
words = set()  
for eng, chn in cut_data:  
    words.update(eng)  
    words.update(chn)
words = ["<pad>", "<unk>", "<start>", "<end>"] + list(words)  # 添加特殊标记
vocab_size=len(words)
word_to_index = {word: i for i, word in enumerate(words)}
index_to_word = {i: word for word, i in word_to_index.items()}
print("Vocabulary size:",vocab_size)

# 将训练数据转换为索引  
indexed_data = []  
for eng, chn in cut_data:  
    eng_indices = [word_to_index[word] for word in eng]  
    chn_indices = [word_to_index["<start>"]] + [word_to_index[word] for word in chn] + [word_to_index["<end>"]]  
    indexed_data.append((eng_indices, chn_indices))  

# 创建数据集和数据加载器  
dataset = TranslationDataset(indexed_data)  
dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True, collate_fn=lambda x: x)  

# 初始化模型、损失函数和优化器  
model = SimpleTransformer(vocab_size, D_MODEL, NHEAD)
criterion = nn.CrossEntropyLoss(ignore_index=word_to_index["<pad>"])  # 忽略 <pad> 标记  
optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)  

# 训练模型
if not torch.cuda.is_available():
    print("CUDA is unavailable, using CPU instead")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")  
model.to(device)  

for epoch in range(EPOCHS):  
    model.train()  
    total_loss = 0  

    for batch in dataloader:  
        src, tgt = zip(*batch)  
        src = nn.utils.rnn.pad_sequence(src, batch_first=False, padding_value=word_to_index["<pad>"]).to(device)  
        tgt = nn.utils.rnn.pad_sequence(tgt, batch_first=False, padding_value=word_to_index["<pad>"]).to(device)  

        tgt_input = tgt[:-1, :]  # 去掉最后一个词  
        tgt_output = tgt[1:, :]  # 去掉第一个词  

        optimizer.zero_grad()  
        output = model(src, tgt_input)  # (seq_len, batch_size, vocab_size)  
        output = output.view(-1, vocab_size)  
        tgt_output = tgt_output.reshape(-1)  
        loss = criterion(output, tgt_output)  
        loss.backward()  
        optimizer.step()  

        total_loss += loss.item()  

    print(f"Epoch {epoch + 1}/{EPOCHS}, Loss: {total_loss / len(dataloader)}")  

print("训练完成！")  

# 测试模型  
def translate(model, sentence):  
    model.eval()  
    with torch.no_grad():  
        input_indices = [word_to_index.get(word.lower(), word_to_index["<unk>"]) for word in sentence]  
        print(input_indices)
        input_tensor = torch.tensor(input_indices).unsqueeze(1).to(device)  # (seq_len, batch_size)  

        tgt_input = torch.tensor([word_to_index["<start>"]]).unsqueeze(1).to(device)  # 初始目标输入  
        translated_sentence = []  

        for _ in range(MAX_LEN):  
            output = model(input_tensor, tgt_input)  # (seq_len, batch_size, vocab_size)  
            next_word = output[-1, 0].argmax(dim=-1).item()  # 取最后一个时间步的输出
            if next_word == word_to_index["<end>"]:  
                break  
            translated_sentence.append(index_to_word[next_word])  
            tgt_input = torch.cat([tgt_input, torch.tensor([[next_word]]).to(device)], dim=0)  

        print(translated_sentence)
        return translated_sentence  

while True:
    # 测试翻译  
    test_sentence = input("请输入英文句子: ").split()
    if not test_sentence:continue
    translated = translate(model, test_sentence)  
    print("翻译结果:", " ".join(translated))