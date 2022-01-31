"""鼠标控制器"""
import tkinter as tk
import tkinter.ttk as ttk
from event.mouse import *

def main():

	def dec(func):
		def _(event):
			x,y=func(*getpos())
			goto(x,y)
		return _

	@dec
	def up(x,y):return x,y-int(dt.get())
	@dec
	def down(x,y):return x,y+int(dt.get())
	@dec
	def left(x,y):return x-int(dt.get()),y
	@dec
	def right(x,y):return x+int(dt.get()),y

	root=tk.Tk()
	root.resizable(False,False)
	root.title("鼠标控制器")

	instruction="""说明: 按Alt+Tab键切换到本窗口,
	按↑,↓,←,→键移动鼠标,
	按Enter键单击鼠标,
	按Shift+Enter键右键单击鼠标,
	按Alt+Enter键双击鼠标。"""
	tk.Label(root,text=instruction).pack()
	tk.Label(root,text="鼠标移动速度: ").pack(side=tk.LEFT)
	dt=ttk.Spinbox(root,from_=1,to=100)
	dt.set(8)
	dt.pack()

	root.bind("<Key-Up>",up)
	root.bind("<Key-Down>",down)
	root.bind("<Key-Left>",left)
	root.bind("<Key-Right>",right)
	root.bind("<Key-Return>",lambda event:click())
	root.bind("<Shift-Return>",lambda event:right_click())
	root.bind("<Alt-Return>",lambda event:dblclick())

	root.mainloop()

if __name__=="__main__":main()
