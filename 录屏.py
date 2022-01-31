import tkinter as tk
import tkinter.filedialog as dialog
import time
from PIL import Image,ImageGrab
import numpy as np
import cv2

def select_area():
    area=[0,0,0,0]
    rectangle_id=None
    def _press(event):
        area[0],area[1]=event.x,event.y
    def _move(event):
        nonlocal tip_id,rectangle_id
        cv.delete(tip_id)
        tip_id=cv.create_text((event.x+8,event.y),text="拖曳选择录制区域",
                               anchor = tk.W,justify = tk.LEFT)
    def _drag(event):
        nonlocal rectangle_id
        if rectangle_id is not None:cv.delete(rectangle_id)
        rectangle_id=cv.create_rectangle(area[0],area[1],
                                         event.x,event.y)
        _move(event)
    def _release(event):
        area[2],area[3]=event.x,event.y
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
    window.bind('<Motion>',_move)
    window.bind('<B1-Motion>',_drag,)
    window.bind('<B1-ButtonRelease>',_release)
    window.mainloop()
    return area

def main():
    def _stop():
        nonlocal flag
        flag=True
        btn_stop['state']=tk.DISABLED
        root.title('录制已结束')

    root=tk.Tk()
    root.title('录屏工具')
    btn_stop=tk.Button(root,text='停止',command=_stop)
    btn_stop.pack()
    lbl_fps=tk.Label(root,text='fps:0')
    lbl_fps.pack(fill=tk.X)
    filename=dialog.asksaveasfilename(master=root,
                filetypes=[("avi视频","*.avi"),("所有文件","*.*")],
                defaultextension='.avi')
    if not filename.strip():return

    area=select_area()

    root.title('录制中')
    fps=10;flag=False
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    videoWriter = cv2.VideoWriter(filename, fourcc, fps,
                                  (area[2]-area[0],area[3]-area[1]))
    start=last=time.perf_counter()
    count=0
    while not flag:
        image=ImageGrab.grab(area)
        frame = cv2.cvtColor(np.asarray(image),cv2.COLOR_RGB2BGR)
        videoWriter.write(frame)
        count+=1
        end=time.perf_counter()
        time.sleep(max(count/fps-(end-start),0))
        lbl_fps['text']='fps:'+str(1/(end-last))
        last=end
        root.update()
    videoWriter.release()

if __name__=="__main__":main()
