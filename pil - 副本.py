#import numpy as np
from tkinter import *
from PIL import Image,ImageTk

angle = 20
def animate():
    global imtk,image,id
    for i in range(50):
        image=image.rotate(angle)
    imtk=ImageTk.PhotoImage(image)
    cv.delete(id)
    id=cv.create_image(120,120,image=imtk) #,anchor = 'nw')
    cv.after(2,animate)

root=Tk()
cv=Canvas(root,bg='black')
cv.pack(side=TOP,expand=True,fill=BOTH)
image=Image.open("1.jpg","r")
imtk=ImageTk.PhotoImage(image)
id=cv.create_image(100,100,image=imtk)
cv.after(20,animate)

root.mainloop()
