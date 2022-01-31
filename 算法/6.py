import random

while True:
    a=random.randint(1,100)
    b=random.randint(1,100)

    cod=input('Enter + or - or * or / or q:')
    if cod=='+':

        print("a=", a,", b=", b, "a+b=", a+b)

    elif cod=='-':

        print("a=", a,", b=", b, "a-b=", a-b)

    elif cod=='*':

        print("a=", a,", b=", b, "a*b=", a*b)

    elif cod=='/':

        print("a=", a,", b=", b, "a/b=", a/b)

    elif cod=='q':

        break

    else:

        print('Only enter +,-,*,/,q')
