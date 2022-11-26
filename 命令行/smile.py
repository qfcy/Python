"笑脸程序"
import sys,os,random,time
try:
    import console_tool
except ImportError:console_tool=None
from random import choice

__email__="3076711200@qq.com"
__author__="七分诚意 qq:3076711200"
__version__="1.0"
try:
    SCREEN_SIZE=os.get_terminal_size().columns
except (ValueError,OSError): # ValueError: bad file descriptor
    SCREEN_SIZE=80

COLORS="123456777789ABCDEF"
BACKCOLORS="0012"
SECS=[0.4]*10+[0]*250
big_smileicon="""
                     ..................                                        
                  .                      .                                     
                 .                        .                                    
                .                          .                                   
               .        .         .         .                                  
               .                            .                                  
               .                            .                                  
               .                            .                                  
               .                            .                                  
               .                            .                                  
               .                            .                                  
               .                            .                                  
               .        .         .         .                                  
               .         .........          .                                  
                .                          .                                   
                 .                        .                                    
                  .                      .                                     
                    ....................                                       

""".replace('.','\x01')


def change_color():
    "改变整个命令行窗口的颜色"
    arg=random.choice(COLORS)+random.choice(BACKCOLORS)
    os.system("color "+arg)

def smile():
    for second in SECS:
        print("\x01 \x02 "*(SCREEN_SIZE//4-1)+"\x01")
        change_color()
        time.sleep(second)

def colorful_smile(consolescreen):
    for second in SECS:
        consolescreen.ctext("\x01 \x02"*(SCREEN_SIZE//3)+"  ",choice(console_tool.RAINBOW),
                      choice(console_tool.RAINBOW),reset=False,end="")
        time.sleep(second)

def big_smile(consolescreen):
    count=0
    rainbow=console_tool.RAINBOW[:-1]
    for line in big_smileicon.splitlines():
        color=rainbow[count]
        consolescreen.ctext(line,"white",color)
        count+=1
        if count>=len(rainbow):count=0
        time.sleep(0.04)
        
def main():
    big="--small" not in sys.argv
    small="--big" not in sys.argv
    classic="--classic" in sys.argv
    if console_tool:
        c=console_tool.Console()
        c.colorize(stdout=None)
    else:c=None
    try:
        if small:
            if c and not classic:colorful_smile(c)
            else:smile()
        if big and console_tool:
            for i in range(4):
                big_smile(c)
    except KeyboardInterrupt:
        print("{:-^80}".format("BYE!"),file=sys.stderr)
        os.system("color")

if __name__=="__main__":main()