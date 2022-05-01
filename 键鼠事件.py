import time,sys
import pyWinhook as pyHook
import pythoncom

def OnMouseEvent(event):
    print('鼠标事件: %s (%d)' % (event.MessageName,event.Message))
    print('时间: %s' % time.asctime()) # 或event.Time
    print('窗口: %d (%s)' % (event.Window,event.WindowName))
    print('位置: (%d, %d)' % event.Position)
    print('滚轮状态: %d' % event.Wheel)
    print('注入: %s' % event.Injected)
    print('---')
    sys.stdout.flush()

    # return True to pass the event to other handlers
    # return False to stop the event from propagating
    return True

def SimpleMouseEv(event):
    print("鼠标事件 %s:(%d, %d)" % (event.MessageName,)+event.Position)
    print('时间: %s' % time.asctime())
    print('窗口: %s' % event.WindowName)
    print('---')
    sys.stdout.flush()
    return True

def OnKeyEvent(event):
    print('键盘事件: %s (%d)' % (event.MessageName,event.Message))
    print('时间: %s' % time.asctime())
    print('窗口: %d (%s)' % (event.Window,event.WindowName))
    print('Ascii码: %d (%s)' %  (event.Ascii, chr(event.Ascii)))
    print('键: %s (%d)' %  (event.Key,event.KeyID))
    print('扫描码: %s' %  event.ScanCode)
    print('扩展信息: %s' %  event.Extended)
    print('注入: %s' % event.Injected)
    print('Alt: %s' %  event.Alt)
    print('转变: %s' %  event.Transition)
    print('---')
    sys.stdout.flush()

    return True

def SimpleKeyEv(event):
    print("键盘事件: %s (ascii: %d %s)"%(event.Key,
                                     event.Ascii,chr(event.Ascii)))
    print('---')
    sys.stdout.flush()
    return True

def main():
    global hm
    sys.stdout=open('event.log','w',encoding='utf-8')
    # create the hook mananger
    hm = pyHook.HookManager()
    # register two callbacks
    hm.MouseAllButtonsDown = OnMouseEvent
    hm.MouseWheel = SimpleMouseEv
    hm.KeyDown = SimpleKeyEv

    # hook into the mouse and keyboard events
    hm.HookMouse()
    hm.HookKeyboard()
    pythoncom.PumpMessages()

if __name__ == '__main__':main()
    
