"""使用turtle模块制作的一款游戏。
游戏玩法:在命令行中输入py -m catch_turtle,
这将弹出一个窗口; 点击"开始游戏"按钮,开始游戏。

按↑,↓,←,→键移动玩家,使其触碰被追逐者。触碰即追逐成功，一次得10分,
追逐时，请小心红色的"敌人",触碰"敌人"即追逐失败。
触碰后,被追逐者将会回到原位。每得到40分升一级。
游戏结束后上一次的等级、最高分将会被保存,但分数不会保存,失败后分数清零。
"""
import sys

__email__="3076711200@qq.com"
__author__="七分诚意 qq:3076711200"
__version__="1.1.3"

try:
    try: import catch_turtle.catch_turtle as catch_turtle
    except ImportError: import catch_turtle
except ImportError as err:
    message="错误:找不到游戏核心模块: %s"%err.name
    print(message,file=sys.stderr)

#相当于from xxmodule import *
scope=globals()
for attr in dir(catch_turtle):
    if not attr.startswith('_'):
        obj=getattr(catch_turtle,attr)
        #过滤turtle模块中的函数
        if not getattr(obj,"__module__",None)=="turtle":
            scope[attr]=obj

if __name__=='__main__':start()
