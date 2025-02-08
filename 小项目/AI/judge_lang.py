import sys,os,warnings
import pickle,pickletools
from collections import Counter

PY_FILE=[".py",".pyw"]
CPP_FILE=[".c",".cpp",".h",".hpp"]
MIN_SIZE=8192 # 避免过小的文件影响训练效果
EPOCHS=200
class Perceptron:
    def __init__(self, input_size, learning_rate=0.01):
        # 初始化权重和偏置
        self.weights = [0.0] * input_size
        self.bias = 0.0
        self.learning_rate = learning_rate

    def linear_output(self, x):
        return sum(w * xi for w, xi in zip(self.weights, x)) + self.bias
    def predict(self, x):
        # 计算线性输出
        linear_output=self.linear_output(x)
        return 1 if linear_output >= 0 else 0
    def compute_loss(self, y_true, y_pred):
        # 计算均方误差损失
        return sum((y_t - y_p) ** 2 for y_t, y_p in zip(y_true, y_pred)) / len(y_true)
    def train(self, X, y, epochs=EPOCHS):
        loss = self.test(X, y)
        print(f"Epoch 0/{epochs}, Loss: {loss}") # 训练前

        for epoch in range(epochs):
            predictions=[]
            for i in range(len(X)):
                prediction = self.predict(X[i])
                predictions.append(prediction)
                # 更新权重和偏置
                update = self.learning_rate * (y[i] - prediction)
                self.weights = [w + update * xi for w, xi in zip(self.weights, X[i])]
                self.bias += update

            loss = self.compute_loss(y, predictions)
            print(f"Epoch {epoch + 1}/{epochs}, Loss: {loss}")
    def test(self, X, y):
        predictions=[self.predict(x) for x in X]
        return self.compute_loss(y, predictions)

def extract_freq(file_path):
    with open(file_path, 'rb') as file:
        content = file.read()

    ascii_chars = [chr(char) for char in content if 32 <= char < 128]
    total_chars = len(ascii_chars)
    if total_chars == 0:
        return [0.0] * 96  # ASCII 32-127有96个字符
    frequency = Counter(ascii_chars)
    return [(frequency.get(chr(i), 0) / total_chars) for i in range(32, 128)]

def endswith(string,suffixes):
    return any(string.endswith(suffix) for suffix in suffixes)
def prepare_data(source_paths,minsize=MIN_SIZE):
    file_paths = [];labels = []
    cnt=0
    for file in directories(source_paths):
        cnt+=1
        file=file.lower()
        try:
            if os.path.getsize(file) < minsize: # 小于最小文件大小
                continue
        except OSError:continue
        if endswith(file,PY_FILE+CPP_FILE):
            if endswith(file,PY_FILE):labels.append(1)
            else:labels.append(0)

            file_paths.append(file)
            if len(file_paths)%1000==0:
                print("Collected %d files in %d files"%(len(file_paths),cnt))

    X = []
    for i in range(len(file_paths)):
        X.append(extract_freq(file_paths[i]))
        if (i+1) % 1000 == 0:
            print("Read %d files" % (i+1))
    return X, labels

def train_model(perceptron,source_paths,epochs=EPOCHS,minsize=MIN_SIZE):
    X, y = prepare_data(source_paths,minsize)
    print("Train data: c/c++: %d python: %d" % (y.count(0),y.count(1)))

    perceptron.train(X, y, epochs)

def test_model(perceptron,source_paths,minsize=MIN_SIZE):
    X, y = prepare_data(source_paths,minsize)
    print("Test data: c/c++: %d python: %d" % (y.count(0),y.count(1)))
    print("Loss:",perceptron.test(X, y))

def directories(paths,dirs=True,files=True):
    for path in paths:
        for root,_dirs,_files in os.walk(path):
            if dirs:
                for name in _dirs:
                    yield os.path.join(root, name)
            if files:
                for name in _files:
                    yield os.path.join(root, name)

def print_usage():
    print("Usage：python %s <file or folder> [--model <model file>]"%sys.argv[0])
MODEL_FILE="data/judge_lang.pkl"
SOURCE_PATHS=["E:\\C++","E:\\python"]
def main():
    if len(sys.argv) < 2:
        print_usage();return

    if "--model" in sys.argv:
        index=sys.argv.index("--model")
        if index>=len(sys.argv)-1:
            print_usage();return
        model=sys.argv[index+1]
        del sys.argv[index:index+2]
    else:
        model=MODEL_FILE

    if os.path.isfile(model): # 加载已有的模型
        print("Loading model from %s"%model)
        with open(model,"rb") as f:
            perceptron=pickle.load(f)
    else: # 模型不存在，训练新的模型
        print("Training model from %s"%SOURCE_PATHS)
        perceptron = Perceptron(input_size=96)
        train_model(perceptron,SOURCE_PATHS)
        with open(model,"wb") as f:
            data=pickle.dumps(perceptron)
            f.write(pickletools.optimize(data))

    for i in range(96):
        char=i+32
        print("%c: %7.4f " % (char,perceptron.weights[i]),end="")
        if (i+1)%8==0:print()
    print()

    for path in sys.argv[1:]:
        if os.path.isdir(path):
            print("Testing model from %s"%path)
            test_model(perceptron,[path])
        elif os.path.isfile(path):
            input_freq = extract_freq(path)
            linear_output = perceptron.linear_output(input_freq)
            prediction = perceptron.predict(input_freq)

            if prediction == 1:
                print(f"{path} is predicted to be Python code:", linear_output)
            else:
                print(f"{path} is predicted to be C/C++ code:", linear_output)
        else:
            warnings.warn("Invalid path %s" % path)

if __name__ == "__main__":
    main()
