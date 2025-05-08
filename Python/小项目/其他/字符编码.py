"将字符转换为字符编码。"
while True:
    n=input("输入字符:")
    if len(n)==1:print(hex(ord(n)))
    else:
        for i in range(len(n)):
            print(hex(ord(n[i]))+"\t",end='')#逐个显示字符的编码
        print()
