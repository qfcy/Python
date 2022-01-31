# 功能:扫描特定目录(尤其u盘)中的文件
import sys,os,search_file,time,traceback,pprint
sys.stderr=open('debg_scan.log','w')

scanned=False
with open('config3.ini') as f:dir=f.readline().strip()

while 1:
    try:
        if os.path.exists(dir):
            t=time.localtime()
            file=os.path.join(os.getcwd(),'Scan %d-%d-%d.log' % (t.tm_hour,t.tm_min,t.tm_sec))
            if not scanned:
                with open(file,'w') as f:
                    pprint.pprint(list(search_file.directories(dir)),stream=f)
                    sys.stderr.write('Scanned %s\r\n'%dir)
                scanned=True
        else:
            scanned=False
    except:
        traceback.print_exc()
    sys.stderr.flush()
    time.sleep(1)
