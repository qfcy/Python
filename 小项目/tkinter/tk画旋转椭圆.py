# 一种方法是使用算法, 这样速度快
# 另一种以下代码介绍的方法速度慢, 但程序简单
import tkinter as tk
from PIL import ImageTk,ImageGrab
import time

COLOR="#ffeeee"
root=tk.Tk()
# 等待一段时间让窗口出现
root.update()
time.sleep(0.3)


cv=tk.Canvas(root,bg=COLOR)
cv.pack(expand=True,fill=tk.BOTH)
x1,x2,y1,y2 = 40,20,270,200
old = cv.create_oval(x1,x2,y1,y2)
# 画完后需要刷新画布, 否则图形显示不出来
root.update()
xroot,yroot = cv.winfo_rootx(), cv.winfo_rooty()

# 获取截取的图像
# 需要加1, 否则会漏掉椭圆的部分边缘
image=ImageGrab.grab((x1+xroot,x2+yroot,
                     y1+xroot+1,y2+yroot+1))
# 旋转图片, 注意后面的fillcolor和expand参数
new=image.rotate(60,fillcolor=COLOR,expand=True)

# 删除旧的椭圆
cv.delete(old)
# 画回到Canvas
imtk=ImageTk.PhotoImage(new)
cv.create_image(200,140,image=imtk)
root.mainloop()