"使用tkinter.Canvas,模拟扩散运动的程序。"
import time,random,math
import tkinter as tk
import tkinter.ttk as ttk

_NUM=1000 #点数默认为1000
_STARTED=False

def start(canvas,num=_NUM):
    "在画布上的初始位置绘制出多个点。"
    x=int(canvas.winfo_width())//2
    y=int(canvas.winfo_height())//2
    for i in range(num):
        canvas.create_oval(x,y,x,y)

def test(canvas,speed=5,num=_NUM,speed_scale=None):
    #模拟扩散运动的主函数
    start(canvas,num)
    canvas.update()
    try:
        while True:
            if speed_scale:speed=int(speed_scale.get())
            for i in range(num):
                angle = random.uniform(0,360)
                dx=math.cos(angle)*speed
                dy=math.sin(angle)*speed
                canvas.move(i,dx,dy) #移动画布上的点
            canvas.update()
            #time.sleep(0.05)
    except tk.TclError:pass

def main():
    def clicked():
        startbtn["state"]=number["state"]=tk.DISABLED
        test(cv,num=int(number.get()),speed_scale=speed)
    def speed_changed(value):
        speed_label["text"]="    速度: %d"%(eval(value))
    
    root=tk.Tk()
    root.title("test")
    root.state("zoomed")
    #创建画布
    cv=tk.Canvas(root,bg="white")
    cv.pack(expand=True,fill=tk.BOTH)
    options=tk.Frame(root)
    startbtn=ttk.Button(options,text="开始",
                        command=clicked)
    startbtn.pack(side=tk.LEFT)
    speed_label=tk.Label(options)
    speed_label.pack(side=tk.LEFT)
    #创建速度滑块
    speed=ttk.Scale(options,from_=0,to=50,length=200,
                    orient=tk.HORIZONTAL,command=speed_changed)
    speed.set(5)
    speed.pack(side=tk.LEFT)
    tk.Label(options,text="    点数: ").pack(side=tk.LEFT)
    number=ttk.Entry(options)
    number.insert(tk.INSERT,str(_NUM))
    number.pack(side=tk.LEFT)
    options.pack()

    root.mainloop()

if __name__=="__main__":main()
