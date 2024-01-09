class Perceptron:
    def __init__(self,eta=0.01,iterations=10):
        self.lr=eta
        self.iterations=iterations
        self.w=0
        self.bias=0
    def fit(self,X,Y):
        for _ in range(self.iterations):
            for i in range(len(X)):
                x=X[i];y=Y[i]
                update=self.lr*(y-self.predict(x))
                self.w+=update*x
                self.bias+=update
            print("w=",self.w,",bias=",self.bias)
    def net_input(self,x):
        return self.w*x+self.bias
    def predict(self,x):
        #return 1 if self.net_input(x)>0 else 0
        return self.net_input(x)

x=[1,2,3,4,5,0,-1,-10]
y=[0,1,2,3,4,-1,-2,-11]

model=Perceptron(0.01,100)
model.fit(x,y)

test_x=[2,3,-1]
for x in test_x:
    print(x,model.predict(x))

print("w=",model.w,",bias=",model.bias)