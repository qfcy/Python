import tkinter as tk
import tkinter.messagebox as msgbox
from PIL import Image,ImageTk

COLOR='#f0f0f0' # 设置这个颜色值可隐藏canvas边框

root=tk.Tk()
root.wm_attributes('-transparentcolor', COLOR)
root["bg"]=COLOR
root.title("透明窗体")
root.overrideredirect(True)
#root.attributes("-alpha",0.5)

cv=tk.Canvas(root)
cv.pack(expand=True,fill=tk.BOTH)
cv["bg"]=COLOR
pic=Image.open("图标\\snake.ico","r").resize((100,100))
imtk=ImageTk.PhotoImage(pic)
x,y=250,200
root.geometry('%dx%d+%d+%d'%(pic.width,pic.height,x,y))
cv.create_image(0,0,image=imtk,anchor=tk.NW)

msgbox.showinfo("","点击图标, 再按Alt+F4键关闭。",master=root)
root.focus_force()
root.mainloop()
