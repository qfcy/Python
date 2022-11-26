# 该项目为beta版本, 录制按键功能待完善
import time,sys
import pyWinhook as pyHook
import pythoncom

MOUSE_ACCURACY = 5 # 鼠标精确度, 单位像素
last_pos = None
def _check_accuracy(new_pos): # 检测鼠标精确度
    global last_pos
    if last_pos is None:
        last_pos = new_pos
        return True
    last_x,last_y = last_pos
    new_x,new_y = new_pos
    if abs(last_x - new_x) > MOUSE_ACCURACY or \
       abs(last_y - new_y) > MOUSE_ACCURACY:
        last_pos = new_pos
        return True
    else:
        return False
def _timer(): # 用于计时, 打印time.sleep代码
    global last_time
    # 0.001秒: 用于补偿调用API函数消耗的时间
    tm=time.perf_counter()-last_time-0.001
    if tm > 0:
        print('time.sleep(%f)'%tm)
    last_time = time.perf_counter()


def left_down(event):
    _timer()
    print('mouse.leftdown()')
    sys.stdout.flush()
    # return True to pass the event to other handlers
    # return False to stop the event from propagating
    return True

def middle_down(event):
    _timer()
    print('mouse.middledown()')
    sys.stdout.flush()
    return True
def right_down(event):
    _timer()
    print('mouse.rightdown()')
    sys.stdout.flush()
    return True

def left_up(event):
    _timer()
    print('mouse.leftup()')
    sys.stdout.flush()
    return True
def middle_up(event):
    _timer()
    print('mouse.middleup()')
    sys.stdout.flush()
    return True
def right_up(event):
    _timer()
    print('mouse.rightup()')
    sys.stdout.flush()
    return True

def mouse_move(event):
    if _check_accuracy(event.Position):
        _timer()
        print('mouse.move(%d, %d)'%event.Position)
    sys.stdout.flush()
    return True

def mouse_wheel(event):
    _timer()
    print('mouse.wheel(%d*mouse.WHEEL_DELTA)'%event.Wheel)
    sys.stdout.flush()
    return True

def key_down(event):
    _timer()
    print('key.down(%s)'%repr(event.Key))
    sys.stdout.flush()
    return True
def key_up(event):
    _timer()
    print('key.up(%s)'%repr(event.Key))
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
    
