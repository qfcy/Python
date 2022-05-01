#使用curse模块制作的文本编辑器
import curses,sys
from curses.textpad import Textbox, rectangle
import msgbox
msgbox.init()

def main(stdscr):
    curses.start_color()
    curses.init_pair(1,curses.COLOR_GREEN,curses.COLOR_BLACK)
    
    stdscr.addstr(0, 0, "Enter Filename to edit:",curses.color_pair(1))
    curses.echo()
    filename = stdscr.getstr(1,0)
    stdscr.addstr(2, 0, "Enter text: (hit Ctrl-G to save)",curses.color_pair(1))
    editwin = curses.newwin(22,80,3,0)
    stdscr.refresh()
    curses.noecho()
    
    box = Textbox(editwin)
    try:
        f=open(filename,'rb')
        for char in f.read():
            box._insert_printable_char(char)
    except FileNotFoundError:pass
    
    # Let the user edit until Ctrl-G is struck.
    box.edit()

    # Get resulting contents
    text = box.gather()
    try:
        f=open(filename,'w')
        f.write(text)
        f.close()
    except OSError:
        print("Invalid filename: %r"%str(filename,encoding="utf-8"),file=sys.stderr)

curses.wrapper(main)
