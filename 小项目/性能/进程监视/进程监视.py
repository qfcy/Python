import sys,os,ctypes,time
import psutil
try:
    from shlex import join as join_args
except ImportError:
    def join_args(*args):
        return " ".join(f'"{arg}"' if ' ' in arg else arg for arg in args)

INTERVAL = 0.05
def main():
    # 初始化 PID 记录
    previous_pids = set()
    previous_process_info = {}  # 用于存储进程信息
    first = True  # 首次

    while True:
        start_time = time.perf_counter() # 开始时间
        # 获取当前所有进程
        current_pids = set()
        added_processes = []

        # 遍历所有进程
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            pid = proc.info['pid']
            current_pids.add(pid)
            previous_process_info[pid] = {
                'name': proc.info['name'],
                'cmdline': proc.info['cmdline'] if proc.info['cmdline'] else ['(未知)']
            }

            if pid not in previous_pids:
                # 新增进程，记录详细信息
                added_processes.append({
                    'pid': pid,
                    'name': proc.info['name'],
                    'cmdline': proc.info['cmdline'] if proc.info['cmdline'] else ['(未知)']
                })

        # 计算新增和移除的 PID
        removed_pids = previous_pids - current_pids

        # 输出新增进程信息
        if added_processes and not first:
            for proc in added_processes:
                print(f"""新增进程 PID: {proc['pid']} 名称: {proc['name']} \
命令行: {join_args(*proc['cmdline'])}""")

        # 输出移除的 PID
        if removed_pids:
            for pid in removed_pids:
                if pid in previous_process_info:
                    proc_info = previous_process_info[pid]
                    print(f"""进程结束 PID: {pid} 名称: {proc_info['name']} \
命令行: {join_args(*proc_info['cmdline'])}""")

        # 更新 previous_pids 为当前进程列表
        previous_pids = current_pids

        # 延迟
        time.sleep(max(INTERVAL - (time.perf_counter()-start_time),0))
        first = False

def is_admin():
    return ctypes.windll.shell32.IsUserAnAdmin()

if __name__ == "__main__":
    if not is_admin(): # 自动以管理员身份运行
        print("Re-run with admin ...")
        pauser=os.path.join(os.path.split(__file__)[0],"console_pauser.py")
        ctypes.windll.shell32.ShellExecuteW(None,"runas", sys.executable,
                                            join_args(*([pauser]+sys.argv)), None, 1)
        sys.exit()
    main()