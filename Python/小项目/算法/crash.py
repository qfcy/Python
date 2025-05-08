import sys
sys.setrecursionlimit(10000)

def crash(n=1,print_times=False):
    if print_times:print(n)
    return crash(n+1,print_times)

if __name__=="__main__":
    crash(print_times=True)
