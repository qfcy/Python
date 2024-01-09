import sys,os
def find_dir():
    for path in sys.path:
        if path.lower().endswith("lib"):return path

print("Starting turtledemo...")
path=find_dir()+r'\turtledemo\__main__.py'
print(path)
os.system("py "+path)
