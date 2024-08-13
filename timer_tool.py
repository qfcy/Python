"""A Python timer module, containing class Timer() and decorator function timer(), 
as well as some useful functions that can be used for performance analysis.
一个Python计时器模块, 其中包含Timer()类和timer()装饰器, 以及一些相关的有用函数, 可用于程序性能分析。

示例1:
import timer_tool
t=timer_tool.Timer() #初始化Timer对象
do_something()
t.printtime() #输出执行do_something()所用时间 (也可使用t.gettime()获取所用时间)

示例2:
#退出with语句时自动打印出所用时间。
import timer_tool
with timer_tool.Timer(): #在这里开始计时
    do_something()

示例3:
 # 为某个函数计时
from timer_tool import timer
@timer
def func():
    print("Hello World!")

示例4:
# 程序精确地延迟一段时间
from time import sleep
from timer_tool import sleep as sleep2
sleep(0.0001)
sleep2(0.0001)
# 经测试表明, time模块的sleep()函数与本模块的函数相比, 有明显的延迟
"""
import sys, time
import functools
from types import FunctionType
from inspect import isgeneratorfunction

__email__ = "3076711200@qq.com"
__author__ = "qfcy qq:3076711200"
__version__ = "1.2.4"
__all__ = ["Timer","timer","sleep"]

perf_counter = time.perf_counter
class Timer:
    "一个计时器类"

    def __init__(self):
        self.start()

    def start(self):
        "开始计时"
        self.time = perf_counter()

    __enter__ = start

    def gettime(self):
        "获取从计时开始到现在的时间"
        return perf_counter() - self.time

    def printtime(self, fmt_str="用时:{:.8f}秒"):
        "打印gettime获取的值"
        print(fmt_str.format(perf_counter() - self.time))

    def __exit__(self, *args):
        self.printtime()


def timer(msg=None,
          file=sys.stdout, flush=False):
    """一个装饰器, 为某个函数计时 (比使用Timer类更快、更简单)。
用法:@timer(msg="用时:{time}秒")
def func(args):
    print("Hello World!")

#或:
@timer
def func(args):
    print("Hello World!")
"""

    def _wrapper(fun):

        @functools.wraps(fun)
        def _call(*args, **kw):
            start = perf_counter()
            result = fun(*args, **kw)
            t = perf_counter() - start
            print(msg.format(func=fun.__name__, time=t),
                  file=file, flush=flush)
            return result

        # 针对生成器
        @functools.wraps(fun)
        def _gen(*args, **kw):
            avg = 0;
            count = 0
            iter = fun(*args, **kw)
            start = perf_counter()
            for result in iter:
                yield result  # 生成原来生成器的结果
                count += 1
            total = perf_counter() - start
            avg = total / count if count > 0 else total
            print(msg.format(func=fun.__name__, avg=avg, count=count, total=total),
                  file=file, flush=flush)

        return _gen if isgeneratorfunction(fun) else _call

    default_msg = "调用{func}用时:{time:.8f}秒"
    default_gen_msg = "调用{func} 生成单个值平均间隔: {avg:.8f}秒, {count} 个值总用时:{total:.8f}"

    if isinstance(msg, FunctionType):  # 直接使用@timer
        fun = msg
        msg = default_gen_msg if isgeneratorfunction(fun) else default_msg
        return _wrapper(fun)
    else:  # @timer后面括号中还有参数
        msg = msg or (default_gen_msg if isgeneratorfunction(fun) else default_msg)
        return _wrapper


def sleep(seconds): # 精确地等待一段时间
    start = perf_counter()
    while perf_counter()-start < seconds:
        pass

def test1():  # 测试Timer类
    t = Timer()
    t.printtime("调用printtime及启动用时:{:.8f}秒")


@timer
def test2():  # 测试@timer的性能(用于函数)
    pass

_TEST3_LOOPS = 20
@timer
def test3_1():  # 使用了@timer的生成器
    for i in range(_TEST3_LOOPS):
        yield i
        time.sleep(0.02)

def _test3_generator():
    for i in range(_TEST3_LOOPS):
        yield i
        time.sleep(0.02)
@timer
def test3_contrast():  # 对照试验
    list(_test3_generator())


@timer
def test4_contrast(t):  # 对照组, 测试time.sleep()函数
    time.sleep(t)  # 结果是0.01秒, 和test2的结果对照, 说明time模块的sleep()函数有一定延迟
@timer
def test4(t):  # 测试本模块sleep()函数的精确度
    sleep(t)

if __name__ == "__main__":
    print("1.测试Timer()类")
    test1()
    print()
    print("2.测试@timer的性能(用于函数)")
    test2()
    print()
    print("3.测试@timer的性能(用于生成器)")
    list(test3_1())
    test3_contrast()
    print()
    t=0.00005
    print(f"4.测试本模块sleep()函数的精确度，等待{t:.6f}秒")
    test4_contrast(t)
    test4(t)
    print("两者对照, 说明time模块的sleep()函数有一定延迟")