import threading
import time
import random

COUNT = 10
shared_dict = {'last_thread': -1}
done = [False] * COUNT
start = False

def format_list(iterable): # 输出列表为类似[1] * 3 + [2] * 2的格式
    length = 1
    result = []
    iterable=iter(iterable)
    try:pre = next(iterable)
    except StopIteration:
        return "[]"
    for item in iterable:
        if pre == item:
            length += 1
        else:
            result.append(f"[{pre}] * {length}")
            pre = item
            length = 1
    if length > 0:
        result.append(f"[{pre}] * {length}")
    return " + ".join(result)

def modify_dict(thread_id, iterations):
    while not start:pass # 等待开始
    for _ in range(iterations):
        shared_dict['last_thread'] = thread_id # 原子操作
    print(f"Done: {thread_id}")
    done[thread_id] = True

def main():
    global start
    iterations = 100
    threads = []

    for i in range(COUNT):
        thread = threading.Thread(target=modify_dict, args=(i, iterations))
        threads.append(thread)
        thread.start()

    values = []
    start = True # 使所有线程同时开始
    while not all(done):
        values.append(shared_dict['last_thread'])
    print(format_list(values))

if __name__ == "__main__":main()