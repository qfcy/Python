def reverse_p(str,n):

    if n<=1:

        print(str)

    else:

        print(str[-1])

        reverse_p(str[:-1],n-1)



str=input("输入:")

reverse_p(str,len(str))
