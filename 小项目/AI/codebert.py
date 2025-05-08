import os,pprint,traceback
from transformers import RobertaConfig, RobertaTokenizer, RobertaForMaskedLM, pipeline

MODEL_NAME = "microsoft/codebert-base-mlm"

print(f"Loading {MODEL_NAME}")
model = RobertaForMaskedLM.from_pretrained(MODEL_NAME)
tokenizer = RobertaTokenizer.from_pretrained(MODEL_NAME)

if not os.path.isdir(MODEL_NAME):
    model.save_pretrained(MODEL_NAME)
    tokenizer.save_pretrained(MODEL_NAME)


while True:
    code = input("输入代码 (空缺以<mask>表示): ").strip()
    if not code:continue
    try:
        fill_mask = pipeline('fill-mask', model=model, tokenizer=tokenizer)
        outputs = fill_mask(code)
        pprint.pprint(outputs)
    except Exception:
        traceback.print_exc()
