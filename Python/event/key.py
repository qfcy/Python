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
VK_CODE={ # 兼容 PyWinHook库
"lbutton": 1,
"rbutton": 2,
"cancel": 3,
"mbutton": 4,
"backspace": 8,
"back": 8,
"tab": 9,
"clear": 12,
"enter": 13,
"return": 13,
"shift": 16,
"ctrl": 17,
"control": 17,
"alt": 18,
"menu": 18,
"pause": 19,
"caps_lock": 20,
"capital": 20,
"kana": 21,"hangeul": 21,"hangul": 21,
"junja": 23,
"final": 24,
"hanja": 25,"kanji": 25,
"esc": 27,
"escape": 27,
"convert": 28,
"nonconvert": 29,
"accept": 30,
"modechange": 31,
"space": 32,
"page_up": 33,
"pgup": 33,
"prior": 33,
"page_down": 34,
"pgdn": 34,
"next": 34,
"end": 35,
"home": 36,
"left": 37,
"up": 38,
"right": 39,
"down": 40,
"select": 41,
"print": 42,
"execute": 43,
"print_screen": 44,
"prtscr": 44,
"snapshot": 44,
"ins": 45,
"insert": 45,
"del": 46,
"delete": 46,
"help": 47,
"win": 91,
"lwin": 91,
"rwin": 92,
"apps": 93,
"multiply": 106,
"add": 107,
"separator": 108,
"subtract": 109,
"decimal": 110,
"divide": 111,
"num_lock": 144,
"numlock": 144,
"scroll_lock": 145,
"scroll": 145,
"left_shift": 160,
"lshift": 160,
"right_shift": 161,
"rshift": 161,
"left_control": 162,
"lcontrol": 162,
"right_control": 163,
"rcontrol": 163,
"left_menu": 164,
"lmenu": 164,
"right_menu": 165,
"rmenu": 165,
"browser_back": 166,
"browser_forward": 167,
"browser_refresh": 168,
"browser_stop": 169,
"browser_search": 170,
"browser_favorites": 171,
"browser_start_and_home": 172,
"browser_home": 172,
"volume_mute": 173,
"volume_Down": 174,
"volume_down": 174,
"volume_up": 175,
"next_track": 176,
"media_next_track": 176,
"previous_track": 177,
"media_prev_track": 177,
"stop_media": 178,
"media_stop": 178,
"play_media": 179,
"pause_media": 179,
"play/pause_media": 179,
"media_play_pause": 179,
"start_mail": 180,
"launch_mail": 180,
"select_media": 181,
"launch_media_select": 181,
"start_application_1": 182,
"launch_app1": 182,
"start_application_2": 183,
"launch_app2": 183,
";": 186, # 不是字符本身的ASCII码
"=": 187,
",": 188,
"-": 189,
".": 190,
"/": 191,
"`": 192,
"[": 219,
"\\": 220,
"]": 221,
"'": 222,
"oem_1": 186,
"oem_plus": 187,
"oem_comma": 188,
"oem_minus": 189,
"oem_period": 190,
"oem_2": 191,
"oem_3": 192,
"oem_4": 219,
"oem_5": 220,
"oem_6": 221,
"oem_7": 222,
"oem_8": 223,
"oem_102": 226,
"processkey": 229,
"packet": 231,
"attn": 246,
"crsel": 247,
"exsel": 248,
"ereof": 249,
"zoom": 251,
"noname": 252,
"pa1": 253,
"clear": 254,
"oem_clear": 254
}
VK_CODE.update(
    dict([("f%d"%i,0x6F+i) for i in range(1,25)]) # f1-f12(及f13-f24)键
)
VK_CODE.update(
    dict([("numpad_%d"%i,0x60+i) for i in range(10)]) # 小键盘按键
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
            return ord(keycode_or_keyname.upper()) # 单个字符的按键名不区分大小写
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
