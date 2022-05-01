import time,sys
import pyWinhook as pyHook
import pythoncom

def timer():
    global last_time
    # 0.001秒: 用于补偿调用API函数消耗的时间
    tm=time.perf_counter()-last_time-0.001
    if tm > 0:
        print('time.sleep(%f)'%tm)
    last_time = time.perf_counter()

def left_down(event):
    timer()
    print('mouse.leftdown()')
    sys.stdout.flush()
    # return True to pass the event to other handlers
    # return False to stop the event from propagating
    return True

def middle_down(event):
    timer()
    print('mouse.middledown()')
    sys.stdout.flush()
    return True
def right_down(event):
    timer()
    print('mouse.rightdown()')
    sys.stdout.flush()
    return True

def left_up(event):
    timer()
    print('mouse.leftup()')
    sys.stdout.flush()
    return True
def middle_up(event):
    timer()
    print('mouse.middleup()')
    sys.stdout.flush()
    return True
def right_up(event):
    timer()
    print('mouse.rightup()')
    sys.stdout.flush()
    return True

def mouse_move(event):
    timer()
    print('mouse.move(%d, %d)'%event.Position)
    sys.stdout.flush()
    return True

def mouse_wheel(event):
    timer()
    print('mouse.wheel(%d*mouse.WHEEL_DELTA)'%event.Wheel)
    sys.stdout.flush()
    return True

def key_down(event):
    timer()
    print('key.down(%d)'%event.Ascii)
    sys.stdout.flush()
    return True
def key_up(event):
    timer()
    print('key.up(%d)'%event.Ascii)
    sys.stdout.flush()
    return True

def main():
    global last_time,hm
    sys.stdout=open('event.py','w',encoding='utf-8')
    # create the hook mananger
    hm = pyHook.HookManager()

    hm.MouseLeftDown = left_down
    hm.MouseMiddleDown = middle_down
    hm.MouseRightDown = right_down
    hm.MouseLeftUp = left_up
    hm.MouseMiddleUp = middle_up
    hm.MouseRightUp = right_up
    hm.MouseMove = mouse_move
    hm.MouseWheel = mouse_wheel
    hm.KeyDown = key_down
    hm.KeyUp = key_up

    # hook into the mouse and keyboard events
    hm.HookMouse()
    hm.HookKeyboard()
    print("""from event import key,mouse
import time""")
    last_time = time.perf_counter()
    pythoncom.PumpMessages()

if __name__ == '__main__':main()
    
