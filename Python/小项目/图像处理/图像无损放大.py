import os,traceback
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox
import cv2
import numpy as np
from scipy.fftpack import dct, idct

BLOCK_SIZE=128
def dct2(block):
    # 执行二维离散余弦变换
    return dct(dct(block.T, norm='ortho').T, norm='ortho')

def idct2(block):
    # 执行二维离散余弦逆变换
    return idct(idct(block.T, norm='ortho').T, norm='ortho')

def enlarge_channel_dct(channel, scale_factor, block_size):
    """
    对单个颜色通道进行基于DCT的图像放大
    :param channel: 输入的颜色通道（二维numpy数组）
    :param scale_factor: 放大倍数（整数）
    :return: 放大后的颜色通道
    """
    height, width = channel.shape
    new_height, new_width = height * scale_factor, width * scale_factor

    # 初始化放大后的通道
    upscaled = np.zeros((new_height, new_width), dtype=np.float32)

    for i in range(0, height, block_size):
        for j in range(0, width, block_size):
            # 提取块
            block = channel[i:i+block_size, j:j+block_size]
            if block.shape[0] != block_size or block.shape[1] != block_size:
                # 如果块大小不够，则进行填充
                block = np.pad(block, ((0, block_size - block.shape[0]), (0, block_size - block.shape[1])), 'constant')

            # 应用DCT
            dct_block = dct2(block)

            # 放大DCT系数矩阵
            dct_upscaled = np.zeros((block_size * scale_factor, block_size * scale_factor), dtype=np.float32)
            dct_upscaled[:block_size, :block_size] = dct_block

            # 应用逆DCT
            idct_block = idct2(dct_upscaled)

            # 插入放大的块到上采样图像中
            up_i = i * scale_factor
            up_j = j * scale_factor
            # 计算插入的范围，确保不超出边界
            upscaled_height = min(up_i + block_size * scale_factor, new_height)
            upscaled_width = min(up_j + block_size * scale_factor, new_width)

            # 插入放大的块
            upscaled[up_i:upscaled_height, up_j:upscaled_width] = \
                idct_block[:upscaled_height - up_i, :upscaled_width - up_j]

    # 裁剪到新尺寸
    upscaled = upscaled[:new_height, :new_width]
    # Clip values to valid range
    upscaled = np.clip(upscaled*scale_factor, 0, 255) # 补偿亮度
    return upscaled.astype(np.uint8)

def enlarge_image_dct(image, scale_factor, block_size=BLOCK_SIZE):
    """
    对彩色图像进行基于DCT的图像放大
    :param image: 输入的彩色图像（BGR格式）
    :param scale_factor: 放大倍数（整数）
    :return: 放大后的图像（BGR格式）
    """
    # 分离颜色通道
    channels=[]
    for channel in cv2.split(image):
        channels.append(enlarge_channel_dct(channel, scale_factor, block_size))

    # 合并放大后的通道
    upscaled_image = cv2.merge(channels)
    return upscaled_image

class ImageZoom:
    DEFAULT_SCALE=2
    def __init__(self, root):
        self.root = root
        self.source_img = None
        self.setup_ui()

    def setup_ui(self):
        self.root.title("图像无损放大工具")
        self.root.geometry("400x300")
        self.root.resizable(False, False)

        btn_open = ttk.Button(self.root, text="选择图像文件", command=self.select_file, width=20)
        btn_open.pack(pady=10)

        self.lbl_selected = ttk.Label(self.root, text="未选择任何文件", wraplength=380, justify="left")
        self.lbl_selected.pack()

        frame_scale = tk.Frame(self.root)
        frame_scale.pack(pady=10)
        lbl_scale = ttk.Label(frame_scale, text="放大倍数: ")
        lbl_scale.pack(side=tk.LEFT, padx=5)
        self.entry_scale = ttk.Entry(frame_scale, width=5)
        self.entry_scale.insert(0, self.DEFAULT_SCALE)
        self.entry_scale.pack(side=tk.LEFT, padx=5)

        frame_block_size = tk.Frame(self.root)
        frame_block_size.pack(pady=10)
        lbl_block_size = ttk.Label(frame_block_size, text="块大小 (像素): ")
        lbl_block_size.pack(side=tk.LEFT, padx=5)
        self.entry_block_size = ttk.Entry(frame_block_size, width=5)
        self.entry_block_size.insert(0, BLOCK_SIZE)
        self.entry_block_size.pack(side=tk.LEFT, padx=5)

        btn_process = ttk.Button(self.root, text="放大图像并保存", command=self.process_image_and_save, width=20)
        btn_process.pack(pady=10)

    def select_file(self):
        source_img = filedialog.askopenfilename(
            title="选择图像文件",
            filetypes=[("图像文件", "*.jpg *.png *.bmp")]
        )
        if source_img:
            self.source_img = source_img
            self.lbl_selected.config(text=f"已选择文件：\n{source_img}")

    def process_image_and_save(self):
        if not self.source_img:
            messagebox.showerror("错误", "请先选择图像文件！")
            return

        image = cv2.imdecode(np.fromfile(self.source_img, 
                dtype=np.uint8), cv2.IMREAD_UNCHANGED) #解决中文路径问题，原为cv2.imread(self.source_img)
        if image is None:
            messagebox.showerror("错误", "加载图像失败，请重新选择一个有效图像文件！")
            return

        try:
            scale = int(self.entry_scale.get())
            if scale < 1:raise ValueError("scale should be > 1")
            block_size = int(self.entry_block_size.get())
            if block_size < 1:raise ValueError("Block size should be >= 1")
        except Exception as err:
            messagebox.showerror("错误", f"输入错误 ({type(err).__name__}: {str(err)}")
            return

        base, ext = os.path.splitext(self.source_img);ext=ext.lower()
        dest_img = f"{base}_zoom{scale}_{block_size}{ext}"

        try:
            enlarged_image = enlarge_image_dct(image, scale, block_size)
            cv2.imencode(ext, enlarged_image)[1].tofile(dest_img)
        except Exception:
            messagebox.showerror("错误", f"图像处理失败: \n{traceback.format_exc()}")
        else:
            messagebox.showinfo("完成", f"放大图像已保存到: \n{dest_img}")

def main():
    root = tk.Tk()
    app = ImageZoom(root)
    root.mainloop()

if __name__ == "__main__":
    main()