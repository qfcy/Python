class LinearRegression:
    def __init__(self,eta=0.01,iterations=10):
        self.lr=eta
        self.iterations=iterations
        self.w=0
        self.bias=0
    def cost_func(self,X,Y,weight,bias):#损失函数
        n=len(X)
        total_error=0
        for i in range(n):
            total_error+=(Y[i]-(weight*X[i]+bias))**2
        return total_error / n
    def fit(self,X,Y):
        n = len(X)
        for cnt in range(self.iterations):
            dw=0;db=0
            # 调整w和bias
            for i in range(n):
                dw += -2 * X[i] * (Y[i]-(self.w*X[i]+self.bias))
                db += -2 * (Y[i] - (self.w*X[i]+self.bias))
            self.w -= dw / n * self.lr
            self.bias -=  db / n *self.lr

            if cnt%10==0:
                cost=self.cost_func(X,Y,self.w,self.bias)
                print("w=",self.w,",bias=",self.bias,
                      ",cost:",cost,"次数:",cnt+1)
    def predict(self,x): # 激活函数（这里直接是输入）
        return self.w*x+self.bias

x=[1,2,3,4,5,0,-1,-10]
y=[0,1,2,3,4,-1,-2,-11]

model=LinearRegression(0.02,500)
model.fit(x,y)

test_x=[2,3,-1]
for x in test_x:
    print(x,model.predict(x))

print("w=",model.w,",bias=",model.bias)