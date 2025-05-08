from ltp import LTP
import torch
# 初始化LTP
print("初始化 LTP")
ltp = LTP("LTP/tiny")

# 将模型移动到 GPU 上
if torch.cuda.is_available():
    print("GPU 加速可用")
    # ltp.cuda()
    ltp.to("cuda")
else:
    print("GPU 加速不可用")

while True:
    str=input("输入文字：").strip()
    if not str:continue
    if str.lower() in ("exit","quit"):break
    result = ltp.pipeline([str], tasks = ["cws","pos","ner","srl","dep","sdp","sdpg"])
    print("分词：")
    print(result.cws)
    print("词性标注：")
    print(result.pos)
    print("命名实体识别：")
    print(result.ner)
    print("语义角色标注：")
    print(result.srl)
    print("依存句法分析：")
    print(result.dep)
    print("语义依存分析(树)：")
    print(result.sdp)
    print("语义依存分析(图)：")
    print(result.sdpg)
    