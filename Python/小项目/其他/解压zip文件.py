import os,zipfile,sys

for file in os.listdir("."):
    if file.endswith(".zip"):
        z=zipfile.ZipFile(file)
        print(file)
        character=""
        for s in z.namelist():
            try:
                # 可能还需要修改zipfile模块源代码的对应部分
                s=s.encode("cp437").decode("gbk")
            except Exception:
                try:s=s.encode("cp437").decode("utf-8")
                except Exception:pass
            if s.endswith(".pmx"):
                character=s[:-4]
                print(character,file)
        if character and "/" not in character:
            try:
                os.mkdir(character)
                z.extractall(character)
            except FileExistsError:
                print(character,file,"已存在")
            