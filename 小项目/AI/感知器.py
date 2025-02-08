class Perceptron:
    def __init__(self,learning_rate=0.01,iterations=10):
        self.lr=learning_rate
        self.iterations=iterations
        self.w=0
        self.bias=0 # 最早假设经过0,0
    def fit(self,X,Y):
        for _ in range(self.iterations):
            for i in range(len(X)):
                x=X[i];y=Y[i]
                self.w+=self.lr*(y-self.predict(x))*x
                self.bias+=self.lr*(y-self.predict(x))
            print("w=",self.w,",bias=",self.bias)
    def net_input(self,x):
        return self.w*x+self.bias
    def predict(self,x):
        #return 1 if self.net_input(x)>0 else 0
        return self.net_input(x)

x=[2]
y=[1]

model=Perceptron(0.01,100)
model.fit(x,y)

test_x=[2,3,-1]
for x in test_x:
    print(x,model.predict(x))

print("w=",model.w,",bias=",model.bias)