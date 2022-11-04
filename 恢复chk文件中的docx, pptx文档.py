import sys,os,zipfile
file = "F:\\FOUND.000\\FILE0000.CHK" # U盘里面的chk文件一般类似于这个路径

# data可以是U盘里面的chk文件，也可以是读取到的原始磁盘数据
data = open(file,'rb').read()
head=b'PK\x03\x04' # zip、docx、pptx等格式的文件头
mark=b"[Content_Types].xml" # 这个也是docx、pptx等格式的标记
estimated_size=2**26 # 恢复出文件的大小(要大于原来的文件)

# 先找出数据中的文件头
offsets = []
for i in range(len(data)):
    if i % 1000000==0:
        print("已处理 %d 字节"%i) # 显示进度
    if data[i:i+len(head)]==head and \
       data[i+30:i+30+len(mark)]==mark: # 如果符合文件头及mark
        if data[i-1]==0 or i==0: # 如果前一个字节是00
            offsets.append(i)
offsets.append(len(data))

print("恢复文件")
for i in range(len(offsets)-1):
    document = data[offsets[i]:offsets[i]+estimated_size] # 数据从文件头开始，长度大于原来的文件大小
    out = "%ds - recovered.pptx"%i # 也可以是docx或xlsx
    with open(out,'wb') as f: # 
        f.write(document)

    # 用zipfile模块检验恢复出的文档是否正常，因为docx、pptx等格式本质上是zip文件
    try:
        z=zipfile.ZipFile(out)
    except zipfile.BadZipFile:
        os.rename(out,"%d - recovered(bad).pptx"%i)
