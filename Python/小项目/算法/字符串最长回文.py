#题目名称：小艺照镜子
#时间限制：1000ms内存限制：256M
#题目描述:
#已知字符串str。 输出字符串str中最长回文串的长度。

#输入描述：
#输入字符串s.(1<=len(str)<=10000)
def solution(s):
    lst_len=[];j=0 # lst_len保存各个可能的回文串长度
    # 处理奇数长度回文, 如"aba"
    for i in range(len(s)):
        dt = min(i+1,len(s)-i) # 循环的次数
        flag=False # 标识是否已遇到不是回文的字符
        for j in range(dt):
            if s[i+j] != s[i-j]: # 回文两边的字符不相等
                lst_len.append((j-1)*2+1)
                flag=True
                break
        if not flag:lst_len.append(j*2+1)
    # 处理偶数长度回文, 如"ffff"
    for i in range(len(s)):
        dt = min(i+1,len(s)-i+1)
        flag=False
        for j in range(dt):
            if s[i+j-1] != s[i-j]: # 这里变成了i+j-1
                lst_len.append((j-1)*2)
                flag=True
                break
        if not flag:lst_len.append(j*2)

    return max(lst_len)

print(solution("ffff"))
print(solution("abababaffff"))