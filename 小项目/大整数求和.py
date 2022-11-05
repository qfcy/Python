from random import randint
def solution(nums):
    num1,num2=nums
    if len(num1)<len(num2):
        num1,num2=num2,num1
    num2=num2.zfill(len(num1)) # num2 的开头用0填充，使num2的长度等于num1的长度
    result=""
    add=0
    for i in range(-1,-len(num2)-1,-1):
        a1,a2=int(num1[i]),int(num2[i])
        s=a1+a2 + add
        #print(a1,a2,s)
        result = str(s%10) + result
        add=s//10 # 下一位的进位

    # 计算结果加上最后一个进位
#     if len(num1)>len(num2):
#         s=int(num1[-len(num2)-1])+add
#         result=str(s)+result
#     elif add > 0:
    if add > 0:
        result=str(add)+result

    #result=num1[:-len(num2)-1]+result # 加上num1多出来的部分
    return result

for i in range(1000):
    num1,num2=str(randint(0,10000)),str(randint(0,10000))
    result=solution([num1,num2])
    if result != str(int(num1)+int(num2)):
         raise Exception("计算错误: %s %s %s"%(num1,num2,result))
    else:
        print("计算正确: %s %s %s"%(num1,num2,result))