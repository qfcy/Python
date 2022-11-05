def a(list1, list2):

    if list1==[] or list2==[]:return []

    newlist=[list1[0]+list2[0]]

    return newlist + a(list1[1:], list2[1:])

print(a([1,2,3],[4,5,6]))
