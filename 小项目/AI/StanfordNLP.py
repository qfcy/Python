import stanza,os

path=os.path.join(os.path.split(__file__)[0],"stanza_resources")
langs=["en","zh-hans"]
# 下载中、英文模型
if not os.path.isdir(path):
    for lang in langs:
        stanza.download(lang, model_dir=path)

lang=langs[int(input("输入语言序号 (" + ", ".join(
            "%d:%s"%(i,langs[i]) for i in range(len(langs))) + "): "))]
# 加载模型
nlp = stanza.Pipeline(lang,processors="tokenize,pos,lemma,depparse",
                      download_method=None,dir=path) # 禁用检查更新

while True:
    sentence = input("输入文本：") # 输入句子
    if sentence.lower() in ("exit","quit"):break

    # 处理句子
    doc = nlp(sentence)

    # 获取词性标注和句法分析结果
    for sentence in doc.sentences:
        print("\n句法分析结果:")
        for word in sentence.words:
            print("%d:"%word.id, word.text,
                  "词性:", word.pos, "依存:",
                  sentence.words[word.head-1].text, # id是从1开始而不是从0
                  "依存关系类型:",word.deprel)