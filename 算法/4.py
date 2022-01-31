from random import randint

# mylist: 存储年龄的列表

mylist=[]

for i in range(80):

    mylist.append(randint(1,80))

# 统计

total=0

for age in mylist:

    if age<18:total+=1

print("不能上网的人数: ",total)
