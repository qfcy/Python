import sys,os,io
import gpt_2_simple as gpt2

# 模型可以是"124M"、"355M"、"774M"等
model = "124M"
if not os.path.isdir(os.path.join("models",model)):
    # 下载124M模型
    print("下载模型 %s..." % model)
    gpt2.download_gpt2(model_name=model)
else:print("模型 %s 已下载" % model)

# 加载模型
sess = gpt2.start_tf_sess()
gpt2.load_gpt2(sess, model_name=model)

# gpt.generate的参数：generate(sess, run_name='run1', checkpoint_dir='checkpoint', model_name=None, model_dir='models', sample_dir='samples', return_as_list=False, truncate=None, destination_path=None, sample_delim='====================\n', prefix=None, seed=None, nsamples=1, batch_size=1, length=1023, temperature=0.7, top_k=0, top_p=0.0, include_prefix=True)

old_stdout=sys.stdout # 修改sys.stdout,由于gpt2.generate函数会直接打印出文本
# 输入前缀（如：once upon a time），生成文本
prefix = input("输入前缀：")
while prefix.lower() not in ("exit","quit"):
    sys.stdout = io.StringIO()
    gpt2.generate(sess, model_name=model, prefix=prefix, 
                        length=250)
    sys.stdout.seek(0)
    text = sys.stdout.read()

    sys.stdout=old_stdout
    print(text)
    prefix = input("输入前缀：")

gpt2.reset_session(sess) # 关闭会话