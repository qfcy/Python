"""使用ctypes,调用API函数,模拟键盘事件的模块。
示例代码:

#模拟按键Alt+F4关闭当前窗口
from event.key import *
keydown("Alt")
keydown("f4")
keyup("f4")
keyup("alt")
"""
import time
from ctypes import *

__all__=["keydown","keyup","keypress","down","up","press"]
KEYEVENTF_KEYUP=2
VK_CODE = {
'backspace':0x08,
'tab':0x09,
'clear':0x0C,
'enter':0x0D,
'shift':0x10,
'ctrl':0x11,
'alt':0x12,
'pause':0x13,
'caps_lock':0x14,
'esc':0x1B,
'space':0x20,
'page_up':0x21,
'pgup':0x21,
'page_down':0x22,
'pgdn':0x22,
'end':0x23,
'home':0x24,
'left':0x25,
'up':0x26,
'right':0x27,
'down':0x28,
'select':0x29,
'print':0x2A,
'execute':0x2B,
'print_screen':0x2C,
'prtscr':0x2C,
'ins':0x2D,
'del':0x2E,
'delete':0x2E,
'win':0x5B, #windows徽标键
'menu':0x5D,
'help':0x2F,
'multiply_key':0x6A,
'add_key':0x6B,
'separator_key':0x6C,
'subtract_key':0x6D,
'decimal_key':0x6E,
'divide_key':0x6F,
'num_lock':0x90,
'scroll_lock':0x91,
'left_shift':0xA0,
'right_shift':0xA1,
'left_control':0xA2,
'right_control':0xA3,
'left_menu':0xA4,
'right_menu':0xA5,
'browser_back':0xA6,
'browser_forward':0xA7,
'browser_refresh':0xA8,
'browser_stop':0xA9,
'browser_search':0xAA,
'browser_favorites':0xAB,
'browser_start_and_home':0xAC,
'volume_mute':0xAD,
'volume_Down':0xAE,
'volume_up':0xAF,
'next_track':0xB0,
'previous_track':0xB1,
'stop_media':0xB2,
'play_media':0xB3,
'pause_media':0xB3,
'play/pause_media':0xB3,
'start_mail':0xB4,
'select_media':0xB5,
'start_application_1':0xB6,
'start_application_2':0xB7,
'attn_key':0xF6,
'crsel_key':0xF7,
'exsel_key':0xF8,
'play_key':0xFA,
'play':0xFA,
'zoom_key':0xFB,
'zoom':0xFB,
'clear_key':0xFE,
'+':0xBB,
',':0xBC,
'-':0xBD,
'.':0xBE,
'/':0xBF,
'`':0xC0,
';':0xBA,
'[':0xDB,
'\\':0xDC,
']':0xDD,
"'":0xDE,
'`':0xC0}
VK_CODE.update(
    dict([("f%d"%i,0x6F+i) for i in range(1,13)])
)
VK_CODE.update(
    dict([("numpad_%d"%i,0x60+i) for i in range(10)])
)

keybd_event=windll.user32.keybd_event

def __convert(keycode_or_keyname):
    #将按键名称转换为键码值
    if isinstance(keycode_or_keyname,str):
        keyname=keycode_or_keyname.lower().replace(' ','_')
        if keyname in VK_CODE:
            return VK_CODE[keyname]
        else:
            if not len(keycode_or_keyname)==1:
                raise ValueError(
                "{} is not a correct key name".format(keycode_or_keyname))
            return ord(keycode_or_keyname.upper())
    else:return keycode_or_keyname

def keydown(keycode_or_keyname):
    """模拟键按下。
keycode_or_keyname:按键名称或该按键的键码值"""
    keycode=__convert(keycode_or_keyname)
    keybd_event(keycode,0,0,0)
down=keydown

def keyup(keycode_or_keyname):
    """模拟键释放。
keycode_or_keyname:按键名称或该按键的键码值"""
    keycode=__convert(keycode_or_keyname)
    keybd_event(keycode,0,KEYEVENTF_KEYUP,0)
up=keyup

def keypress(keycode_or_keyname,delay=0.05):
    """模拟按键。
keycode_or_keyname:按键名称或该按键的键码值
delay:键按下与释放之间的的间隔时间,间隔时间越小,按键速度越快。"""
    keycode=__convert(keycode_or_keyname)
    keydown(keycode)
    time.sleep(delay)
    keyup(keycode)
    time.sleep(delay)
press=keypress