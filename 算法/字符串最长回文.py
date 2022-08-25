#题目名称：小艺照镜子
#时间限制：1000ms内存限制：256M
#题目描述:
#已知字符串str。 输出字符串str中最长回文串的长度。

#输入描述：
#输入字符串s.(1<=len(str)<=10000)
def sol(s):
    lst_len=[];j=0
    for i in range(len(s)): # 处理奇数长度回文, 如"aba"
        dt = min(i+1,len(s)-i)
        flag=False
        for j in range(dt):
            if s[i+j] != s[i-j]:
                lst_len.append((j-1)*2+1)
                flag=True
                break
        if not flag:lst_len.append(j*2+1)
    for i in range(len(s)): # 处理偶数长度回文, 如"ffff"
        dt = min(i+1,len(s)-i+1)
        flag=False
        for j in range(dt):
            if s[i+j-1] != s[i-j]:
                lst_len.append((j-1)*2)
                flag=True
                break
        if not flag:lst_len.append(j*2)
    #print(lst_len)
    return max(lst_len)

print(sol("ffff"))
print(sol("abababa"))