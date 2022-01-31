"将字符编码转换为字符。"
while True:
    n=str(input("输入字符的编码:"))
    l=n.split()
    for n in l:
        print(chr(int(n)),end="")#逐个显示字符的编码
    print()
