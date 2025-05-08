"将字符编码转换为字符。"
while True:
    n=str(input("输入字符的编码:"))
    l=n.split()
    for n in l:
        try:print(chr(eval("0x"+n)),end="")#逐个显示字符的编码
        except Exception as err:print(type(err).__name__,':',err)
    print()
