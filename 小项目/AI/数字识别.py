import tkinter as tk
import tkinter.ttk as ttk
import tkinter.simpledialog as dialog
import numpy as np
import h5py
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten
from tensorflow.keras.optimizers import Adam

DATASET = "data/digits.h5"

def roll_array(arr, row, col, fill=0):
    # 平移二维数组
    rows, cols = arr.shape
    result = np.full_like(arr, fill)

    # 计算原数组中要取的区域
    src_row_start = max(0, -row)
    src_row_end = rows - max(0, row)
    src_col_start = max(0, -col)
    src_col_end = cols - max(0, col)

    # 计算目标数组要放的位置
    dst_row_start = max(0, row)
    dst_row_end = dst_row_start + (src_row_end - src_row_start)
    dst_col_start = max(0, col)
    dst_col_end = dst_col_start + (src_col_end - src_col_start)

    # 赋值
    result[dst_row_start:dst_row_end, dst_col_start:dst_col_end] = \
        arr[src_row_start:src_row_end, src_col_start:src_col_end]

    return result

def normalize_input(arr): # 去除图像左上方空白，归一化图像到左上角
    # 找到第一个非零行
    row_nonzero = np.any(arr != 0, axis=1)
    if not np.any(row_nonzero):
        return arr  # 全零，直接返回
    row_dt = -np.argmax(row_nonzero)

    # 找到第一个非零列
    col_nonzero = np.any(arr != 0, axis=0)
    col_dt = -np.argmax(col_nonzero)
    return roll_array(arr, row_dt, col_dt)

def train_model(dataset):
    # 加载数据集并准备训练数据
    images = dataset['images'][:]
    for i in range(len(images)):
        images[i] = normalize_input(images[i])
    labels = dataset['labels'][:]

    # 构建一个简单的模型
    model = Sequential()
    model.add(Flatten(input_shape=(10, 10)))  # 输入层，展平 10x10 图像
    model.add(Dense(32, activation='relu'))  # 隐藏层
    model.add(Dense(32, activation='relu'))
    model.add(Dense(10, activation='softmax'))  # 输出层，10 个类别

    # 编译模型，使用 sparse_categorical_crossentropy 作为损失函数
    model.compile(optimizer=Adam(), loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    history = model.fit(images, labels, epochs=50, batch_size=32, verbose=0)

    print(f"已训练模型，精确度: {history.history['accuracy'][-1]*100:.2f}%")
    return model

def recognize_digit(model, input_array):
    arr = np.array(input_array, dtype='i')
    input_data = np.array([normalize_input(arr)], dtype='i').reshape((1,10,10))
    probabilities = model.predict(input_data, verbose=0)
    return probabilities[0]  # 返回概率数组

class DrawingApp:
    def __init__(self, root, dataset=DATASET):
        self.root = root
        self.root.title("简易0-9数字识别")

        # 创建Canvas，用于绘制图形
        self.canvas = tk.Canvas(root, width=300, height=300, bg='white')
        self.canvas.grid(row=0, column=0, rowspan=4)

        # 初始化一个10x10的二维数组
        self.array = [[0] * 10 for _ in range(10)]

        # 创建按钮
        self.recognize_button = ttk.Button(root, text="识别", command=self.recognize)
        self.recognize_button.grid(row=0, column=1, padx=10, pady=10)
        self.clear_button = ttk.Button(root, text="清除", command=self.clear_canvas)
        self.clear_button.grid(row=1, column=1, padx=10, pady=10)
        self.add_dataset_button = ttk.Button(root, text="添加到数据集", command=self.add_to_dataset)
        self.add_dataset_button.grid(row=2, column=1, padx=10, pady=10)

        # 创建Label，显示识别结果
        self.result_label = tk.Label(root, text="识别结果：", width=40, height=2,
                                     anchor=tk.W, wraplength = 280)
        self.result_label.grid(row=3, column=1, padx=10, pady=10)

        # 绑定鼠标事件
        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        self.dataset_file = dataset
        self.dataset = self.model = None
        self.load_dataset()
        if self.dataset["images"].size > 0:
            self.model = train_model(self.dataset)
        else:
            self.model = None
        self.model_is_latest = True
    def paint(self, event):
        # 鼠标拖动时绘制黑色方块，并更新二维数组
        x, y = event.x, event.y
        grid_x, grid_y = x // 30, y // 30  # 每个小格30x30
        if 0 <= grid_x < 10 and 0 <= grid_y < 10:
            if self.array[grid_y][grid_x] == 0:  # 只绘制一次
                self.array[grid_y][grid_x] = 1
                self.canvas.create_rectangle(grid_x * 30, grid_y * 30, 
                                             (grid_x + 1) * 30, (grid_y + 1) * 30,
                                             fill="black", outline="black")

    def on_release(self, event):
        # 鼠标释放
        pass #print(self.array)

    def clear_canvas(self):
        # 清空画布和数组
        self.canvas.delete("all")
        self.array = [[0] * 10 for _ in range(10)]  # 重置二维数组
        self.result_label.config(text="识别结果：")

    def recognize(self):
        # 识别按钮触发的事件
        if not self.model_is_latest:
            self.model = train_model(self.dataset) # 修改数据集后，重新训练模型
            self.model_is_latest = True
        if self.model is None:
            probabilities = [0] * 10
        else:
            probabilities = recognize_digit(self.model, self.array)
        num = max(range(10), key=lambda idx:probabilities[idx])
        # 显示识别结果
        result_text = f"""识别结果：{num} \
({', '.join([f'{i}: {prob:.2f}' for i, prob in enumerate(probabilities)])})"""
        self.result_label.config(text=result_text)
    def add_to_dataset(self):
        # 添加当前数据到数据集中
        # 弹出输入框要求用户输入一个数字
        digit = dialog.askinteger("输入数字", "请输入对应的数字 (0-9):", minvalue=0, maxvalue=9)
        if digit is None:return

        # 将当前数组（10x10）和标签（数字）添加到数据集
        image_data = np.array(self.array, dtype='i')
        label_data = np.array([digit], dtype='i')

        # 将新数据添加到数据集中
        with h5py.File(self.dataset_file, 'a') as f:
            images = f['images']
            labels = f['labels']

            # 扩展数据集
            images.resize((images.shape[0] + 1, 10, 10))
            labels.resize((labels.shape[0] + 1,))
            images[-1] = image_data
            labels[-1] = label_data

            self.dataset["images"] = images[:]
            self.dataset["labels"] = labels[:]

        print(f"已添加数字 {digit} 到数据集并保存")
        self.model_is_latest = False
    def load_dataset(self):
        # 加载现有的h5py数据集
        try:
            with h5py.File(self.dataset_file) as f:
                if 'images' not in f:
                    # 如果数据集不存在，则创建一个新的数据集
                    f.create_dataset('images', (0, 10, 10), maxshape=(None, 10, 10), dtype='i')
                    f.create_dataset('labels', (0,), maxshape=(None,), dtype='i')
                self.dataset = {"images":f["images"][:],"labels":f["labels"][:]}
                print(f"""已加载: {self.dataset_file}
数据集大小: {max(len(self.dataset['images']),len(self.dataset['labels']))} \
样本数: {', '.join(f"{num}: {cnt}" for num, cnt in zip(*np.unique(
self.dataset['labels'], return_counts=True)))}""")
        except OSError:
            self.dataset = {"images": np.array([], dtype="i"),
                            "labels": np.array([], dtype="i")}

if __name__ == "__main__":
    root = tk.Tk()
    app = DrawingApp(root)
    root.mainloop()
