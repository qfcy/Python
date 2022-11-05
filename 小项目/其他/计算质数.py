def Prime(num):

    # 异常处理

    if num<=0:raise ValueError("数值必须大于0")

    for i in range(2,num):

        if num%i==0:return False

    return True
