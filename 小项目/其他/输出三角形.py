import time
try:
    import console
    c=console.Console()
except:c=None

def triangle(char,height,delay=0,color="green",*args,**kwargs):
    for n in range(1,height*2,2):
        line=" "*((height*2-n)//2)*len(char)+char*n
        if c:c.ctext(line,color,*args,**kwargs)
        else:print(line)
        time.sleep(delay)

def main():
    while True:
        char=input("三角形的组成字符:")
        if not char:break
        height=int(input("三角形的高:"))
        triangle(char,height,delay=0.02)

if __name__=="__main__":main()
