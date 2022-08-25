import tkinter as tk
import tkinter.filedialog as dialog
import time
from PIL import Image,ImageGrab
import cv2

def select_area():
    area=[0,0,0,0]
    rectangle_id=None
    def _press(event):
        area[0],area[1]=event.x,event.y
    def _move_label(event,text=None):
        nonlocal tip_id,rectangle_id
        text=text or "拖曳选择录制区域(%d, %d)"%(event.x,event.y)
        cv.delete(tip_id)
        tip_id=cv.create_text((event.x+8,event.y),
                              text=text, anchor = tk.W,justify = tk.LEFT)
    def _drag(event):
        nonlocal rectangle_id
        if rectangle_id is not None:cv.delete(rectangle_id)
        rectangle_id=cv.create_rectangle(area[0],area[1],
                                         event.x,event.y)
        _move_label(event)
    def _release(event):
        area[2],area[3]=event.x,event.y
        _move_label(event,"按Enter键接受, 拖曳可重新选择")
        window.bind_all('<Key-Return>',_accept)
    def _accept(event):
        window.destroy()

    window=tk.Tk()
    window.title("选择录制区域")
    window.protocol("WM_DELETE_WINDOW",lambda:None)# 防止窗口被异常关闭
    cv=tk.Canvas(window,bg='white',cursor="target")
    cv.pack(expand=True,fill=tk.BOTH)
    tip_id=cv.create_text((cv.winfo_screenwidth()//2,
                           cv.winfo_screenheight()//2),
                          text="拖曳选择录制区域",
                            anchor = tk.W,justify = tk.LEFT)
    window.attributes("-alpha",0.6)
    window.attributes("-topmost",True)
    window.attributes("-fullscreen",True)
    window.bind('<Button-1>',_press)
    window.bind('<Motion>',_move_label)
    window.bind('<B1-Motion>',_drag,)
    window.bind('<B1-ButtonRelease>',_release)

    while 1:
        try:
            window.update()
            time.sleep(0.01)
        except tk.TclError:break # 窗口已关闭

    x1, x2 = area[0],area[2] # 区分出左、右和上、下边, 
    if x1 > x2:x1,x2 = x2,x1 # 即允许用户从不同方向拖曳选择
    y1, y2 = area[1],area[3]
    if y1 > y2:y1,y2 = y2,y1
    return [x1, y1, x2, y2]

def main():
    def _stop():
        nonlocal flag
        flag=False
        btn_start['state']=tk.DISABLED
        root.title('录制已结束')
    def _start():
        nonlocal flag
        flag=True
        btn_start['text']='停止'
        btn_start['command']=_stop
    def select():
        nonlocal area
        area = select_area()
        btn_start['state']=tk.NORMAL

    root=tk.Tk()
    root.title('录屏工具')
    btn_select=tk.Button(root,text='选择录制区域',command=select)
    btn_select.pack()
    btn_start=tk.Button(root,text='开始',command=_start,state=tk.DISABLED)
    btn_start.pack()
    lbl_fps=tk.Label(root,text='fps:0')
    lbl_fps.pack(fill=tk.X)

    area=None
    flag=False
    while not flag: # 等待用户点击开始
        root.update()
    root.title('录制中')
    fps=60
    start=last=time.perf_counter()
    lst_image=[]
    while flag:
        image=ImageGrab.grab(area)
        lst_image.append(image)
        end=time.perf_counter()
        time.sleep(max(len(lst_image)/fps-(end-start),0))
        try:
            lbl_fps['text']='fps:'+str(1/(end-last))
            last=end
            root.update()
        except tk.TclError:flag=False # 窗口被关闭时
    for i in range(len(lst_image)):
        lst_image[i].save('%d.png'%i) # 在当前文件夹保存png图像序列

if __name__=="__main__":main()
