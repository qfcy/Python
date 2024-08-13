#import timer_tool # timer_tool.py
import pprint
cache={} # 缓存之前计算的结果，避免重复计算
cnt=0
def _isMatch(s: str, p: str,level=0) -> bool:
    global cnt;cnt+=1
    print("s:",s,"p:",p,"level:",level) # level仅用于调试
    for i in range(len(p)):
        if i+1<len(p) and p[i+1]=="*":
            rest=p[i+2:]
            print("rest:",rest)
            if p[i]==".": # .*
                if not "*" in rest: #后面的字符串没有*号
                    return isMatch(s[len(s)-len(rest):],rest,level+1)
                else:
                    for j in range(i,len(s)+1): # s的子串的左端不断右移（非贪婪匹配，如果左移则为贪婪匹配），逐个检查是否匹配
                        if isMatch(s[j:],rest,level+1):
                            return True
                    return False
            else:
                j=i
                while j<len(s) and s[j]==p[i]:
                    j+=1 # 跳过s中所有为p[i]的字符
                if isMatch(s[j:],rest,level+1): # 匹配后面的部分
                    return True
                else:
                    for k in range(i,j): # 左端不断右移，检查是否匹配
                        if isMatch(s[k:],rest,level+1):
                            return True
                    return False
        else:
            if i>=len(s):
                return False
            elif s[i]!=p[i] and not p[i]==".":
                return False
    if len(p)==len(s):return True # 无*号时，字符串已被全部匹配完
    else:return False
def isMatch(s,p,level=0):
    if (s,p) in cache:
        return cache[(s,p)]
    else:
        result=_isMatch(s,p,level)
        cache[(s,p)]=result
        return result

#t=timer_tool.Timer()
result=isMatch("aaaaaaaaaaaaaaaaaaa","a*a*a*a*a*a*a*a*a*b")
#t.printtime()
print("结果:",result)
print("调用次数:",cnt)
#pprint.pprint(cache)