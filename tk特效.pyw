import tkinter as tk

def main():
    window=tk.Tk()
    window["bg"]="white"
    window.title("屏幕已冻结")
    window.attributes("-alpha",0.5)
    window.attributes("-topmost",True)
    window.attributes("-fullscreen",True)
    print(window.frame())
    window.mainloop()

if __name__=="__main__":main()
