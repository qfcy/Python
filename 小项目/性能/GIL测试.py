import threading
import time

# 定义一个 CPU 密集型任务
def cpu_heavy_task(n):
    s = 0
    for i in range(1,n+1):
        s += i
    return s

# 测试单线程执行时间
def single_thread_test(n, iterations):
    start_time = time.time()
    for _ in range(iterations):
        cpu_heavy_task(n)
    end_time = time.time()
    print(f"Single thread time: {end_time - start_time:.2f} seconds")

# 测试多线程执行时间
def multi_thread_test(n, iterations, num_threads):
    threads = []
    start_time = time.time()

    for _ in range(num_threads):
        thread = threading.Thread(target=lambda: [cpu_heavy_task(n) for _ in range(iterations)])
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    end_time = time.time()
    print(f"Multi-threaded time with {num_threads} threads: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    n = 50000000  # 每个任务的迭代次数
    iterations = 1  # 每个线程执行的任务次数
    num_threads = 4  # 线程数量

    print("Starting single-threaded test...")
    single_thread_test(n, iterations)

    print("\nStarting multi-threaded test...")
    multi_thread_test(n, iterations, num_threads)