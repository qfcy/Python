import os

def find_rank(lst,N):
    # lst:待查找的列表 N:第几名
    lst=lst.copy()
    if N<=0 or N>len(lst):
        return None # 未找到
    n=len(lst)
    rank=-1;cnt=0 # rank:列表末已有多少个排名的数据有序
    while cnt<n and rank<N-1:
        for j in range(n-cnt-1):
            if lst[j+1]<lst[j]:
                lst[j+1],lst[j]=lst[j],lst[j+1]
        cnt+=1
        if cnt==1 or cnt>1 and lst[n-cnt+1]>lst[n-cnt]: # cnt==1为第一次交换，用于处理第一名的情况
            rank+=1 # 如果后面的数据大于前面的数据（不等于），就增加一名当前排名
        print(lst,cnt,rank)

    if rank<N-1: # 如果仍未找到第N名
        result=None
    else:
        result=lst[n-cnt]
    return result

lst=[5,2,22,6,4,7,33,22,7,16]
print("数据:",lst)
N=int(input("输入排名: "))
print("结果:",find_rank(lst,N))
os.system("pause")