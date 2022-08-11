import tkinter as tk
import tkinter.ttk as ttk

import windnd,os

l=[]
def ondrag(filenames):
    for f in filenames:
        l.append(f.decode("ansi"))
        print(f)

def OK():
    os.system('"check_^&_upload.bat" ' + " ".join(l))

root=tk.Tk()

btn=ttk.Button(root,text="OK",command=OK)
btn.pack()

windnd.hook_dropfiles(root,func=ondrag)
root.mainloop()