#功能: 静默复制目录到另一个目录
import sys,os,shutil,time,traceback

sys.stderr=open("debug_2.log","w",encoding='utf-8')
# config2.ini示例:
# E:\path1
# E:\path2

with open("config2.ini") as f:
    src=f.readline().strip()
    dst=f.readline().strip()

try:os.mkdir(dst)
except FileExistsError:pass
except Exception:traceback.print_exc()

print('Waiting',file=sys.stderr)
while not ( os.path.exists(src)):
    time.sleep(0.1)

for d in os.listdir(src):
    src_file=os.path.join(src,d)
    dst_file=os.path.join(dst,d)
    try:
        if not os.path.exists(dst_file):
            if os.path.isdir(src_file):
                shutil.copytree(src_file,dst_file)
            else:
                shutil.copy(src_file,dst_file)
            print('复制 %s 到 %s' % (src_file,dst_file),file=sys.stderr)
    except Exception:
        traceback.print_exc()
        time.sleep(1)

sys.stderr.flush()
