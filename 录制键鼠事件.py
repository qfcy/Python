import time,sys
import pyWinhook as pyHook
import pythoncom

def left_down(event):
    print('mouse.leftdown()')
    sys.stdout.flush()
    # return True to pass the event to other handlers
    # return False to stop the event from propagating
    return True

def middle_down(event):
    print('mouse.middledown()')
    sys.stdout.flush()
    return True
def right_down(event):
    print('mouse.rightdown()')
    sys.stdout.flush()
    return True

def left_up(event):
    print('mouse.leftup()')
    sys.stdout.flush()
    return True
def middle_up(event):
    print('mouse.middleup()')
    sys.stdout.flush()
    return True
def right_up(event):
    print('mouse.rightup()')
    sys.stdout.flush()
    return True

def mouse_move(event):
    print('mouse.move(%d, %d)'%event.Position)
    sys.stdout.flush()
    return True

def mouse_wheel(event):
    print('mouse.wheel(%d*mouse.WHEEL_DELTA)'%event.Wheel)
    sys.stdout.flush()
    return True

def key_down(event):
    print('key.down(%d)'%event.ascii)
    sys.stdout.flush()
    return True
def key_up(event):
    print('key.up(%d)'%event.ascii)
    sys.stdout.flush()
    return True

def main():
    global hm
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
    print('from event import key,mouse')
    pythoncom.PumpMessages()

if __name__ == '__main__':main()
    
