import sys,os,timer
from tkinter import *
from PIL import Image

arr=['@','#','$','%','&','?','*','o','/','{','[','(','|','!','^','~','-','_',':',';',',','.','`',' ']

def toText(imagefile):
    result=''
    t=timer.Timer()
    count=len(arr)
    for h in range(imagefile.size[1]):
        for w in range(imagefile.size[0]):
            pix = imagefile.getpixel((w,h))
            if type(pix) is tuple:
                r,g,b,*other=pix
                # 这个像素透明
                if other==[0]:
                    r=g=b=255
                pix = int(r*0.299+g*0.587+b*0.114)
            result += arr[int(pix/256*count)]
        result+='\r\n'
    t.printtime()
    return result

def main():
    if len(sys.argv)==1:
        scriptname=os.path.split(sys.argv[0])[1]
        print("Usage: %s imagefile1 imagefile2 ..."%scriptname)
        return
    for file in sys.argv[1:]:
        t=timer.Timer()
        imagefile=Image.open(file)
        oldsize=imagefile.size
        imagefile=imagefile.resize((int(imagefile.size[0]*0.9),
                                    int(imagefile.size[1]*0.5)))
        with open(os.path.splitext(file)[0]+".txt",'w') as output:
            text=toText(imagefile)
            output.write(text)
        root=Tk()
        root.geometry("%dx%d" % oldsize)
        root.title("预览")
        txt=Text(root,font=(None,1))
        txt.insert('1.0',text)
        txt.pack(expand=True,fill=BOTH)
    mainloop()

if __name__=="__main__":main()
