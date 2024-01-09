with open("1.txt") as f:
    data=f.read().split(' ')

l=[];temp=[]
for i in range(1,len(data)):
    if i % 3 !=0:
        temp.append(round((float(data[i])+25.0)*10000)/10000)
    else:
        l.append(tuple(temp))
        temp=[]
print(l)