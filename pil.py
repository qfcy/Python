#import numpy as np
from tkinter import *
from PIL import Image,ImageTk

angle = 0
def animate():
    global imtk,angle,id
    angle += 10
    image=old.rotate(angle)
    imtk=ImageTk.PhotoImage(image)
    cv.delete(id)
    id=cv.create_image(100,100,image=imtk) #,anchor = 'nw')
    cv.after(20,animate)

root=Tk()
cv=Canvas(root,bg='black')
cv.pack(side=TOP,expand=True,fill=BOTH)
old=Image.open("图标\\blackhole.jpg","r").resize((100,100))
imtk=ImageTk.PhotoImage(old)
id=cv.create_image(100,100,image=imtk)
cv.after(20,animate)

root.mainloop()
