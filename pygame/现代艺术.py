# 来自其他人书中的项目
import pygame,random,sys
from pygame.colordict import THECOLORS

SCREEN_SIZE=WIDTH,HEIGHT=640,480;BACKCOLOR=255,255,255
def mainloop(screen):
    "主事件循环"
    while True:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                return 0
            elif event.type==pygame.MOUSEBUTTONDOWN:
                draw(screen)

def draw(scr):
    scr.fill(BACKCOLOR)
    availble_colors=list(THECOLORS.keys())
    for n in range(100):
        #随机选择矩形位置和颜色
        width=random.randrange(0,250)
        height=random.randrange(0,100)
        left=random.randrange(0,400)
        top=random.randrange(0,500)
        color = THECOLORS[random.choice(availble_colors)]
        line_width=random.randrange(1,3)
        pygame.draw.rect(scr,color,(left,top,width,height),line_width)
    pygame.display.flip()

def main():
    scr=pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption("现代艺术")
    draw(scr)
    return mainloop(scr)

if __name__=="__main__":sys.exit(main())
