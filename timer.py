"""A simple python timer module to analysis performances.
一个Python计时器模块,其中包含Timer类和timer装饰器, 可用于程序性能分析。

示例1:
import timer
t=timer.Timer() #初始化Timer对象
do_something()
t.printtime() #输出执行do_something()所用时间 (使用t.gettime()获取所用时间更快)

示例2:
import timer
with timer.Timer(): #在这里开始计时
    do_something()
#退出with语句时自动打印出所用时间。

示例3:
from timer import timer
@timer # 为func函数计时
def func():
    print("Hello World!")
"""
import sys,time
import functools
from types import FunctionType
from inspect import isgeneratorfunction

__email__="3076711200@qq.com"
__author__="七分诚意 qq:3076711200"
__version__="1.2.1"

perf_counter=time.perf_counter
class Timer:
    "一个计时器类"
    def __init__(self):
        self.start()
    def start(self):
        "开始计时"
        self.time=perf_counter()
    __enter__=start
    def gettime(self):
        "获取从计时开始之后的时间"
        return perf_counter()-self.time
    def printtime(self,fmt_str="用时:{:.8f}秒"):
        "打印gettime获取的值"
        print(fmt_str.format(perf_counter()-self.time))
    def __exit__(self,*args):
        self.printtime()


def timer(msg=None,
          file=sys.stdout,flush=False):
    """一个装饰器, 为某个函数计时 (比Timer类更快)。
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
        def _call(*args,**kw):
            start=perf_counter()
            result=fun(*args,**kw)
            t=perf_counter()-start
            print(msg.format(func=fun.__name__,time=t),
                  file=file,flush=flush)
            return result
        # 针对生成器
        @functools.wraps(fun)
        def _gen(*args,**kw):
            avg=0;count=1
            iter=fun(*args,**kw)
            st=start=perf_counter()
            for result in iter:
                avg = (avg + (perf_counter()-st)*(count-1))/count
                yield result
                count+=1
                st=perf_counter()
            total=perf_counter()-start
            print(msg.format(func=fun.__name__,avg=avg,time=total),
                  file=file,flush=flush)

        return _gen if isgeneratorfunction(fun) else _call

    default_msg="调用{func}用时:{time:.8f}秒"
    default_gen_msg="调用{func} 生成一个值平均用时:{avg:.8f}秒 总用时:{time:.8f}"

    if isinstance(msg,FunctionType):# 直接使用@timer
        fun=msg
        msg=default_gen_msg if isgeneratorfunction(fun) else default_msg
        return _wrapper(fun)
    else: # @timer后还使用其他参数
        msg=msg or (default_gen_msg if isgeneratorfunction(fun) else default_msg)
        return _wrapper


def test1():
    t=Timer()
    t.printtime("调用printtime及启动用时:{:.8f}秒")

@timer
def test2():pass

@timer
def test3():
    yield 1
    time.sleep(0.5)
    yield 3
    time.sleep(0.1) # 这一行不被计算在平均用时内

if __name__=="__main__":
    list(test3()) # test2() # test1()
