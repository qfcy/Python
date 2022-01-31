# Configuration file for Squish
# -----------------------------

# Feel free to modify the configuration variables below to taste.
# If the game is too fast or too slow, try to modify the speed variables.

#info of game Squish

welcome='''
Welcome to Squish,
the game of Fruit Self-Defense'''

info='''
In this game you are a banana,
trying to survive a course in
self-defense against fruit, where the
participants will "defend" themselves
against you with a 16 ton weight.'''

# Change these to use other images in the game:
banana_image = '香蕉.jpg'
weight_image = '铅锤.jpg'
splash_image = '游戏图标.jpg'

# Change these to affect the general appearance:
screen_size = 800, 600
background_color = 255, 255, 255
margin = 30
full_screen = False
font_size = 48

# These affect the behavior of the game:
drop_speed = 1
banana_speed = 10
speed_increase = 0.2
weights_per_level = 10
banana_pad_top = 40
banana_pad_side = 20
#--------------------------------------------------------------

def main():
    import os
    f=open(os.path.realpath(__file__),'rb')
    while True:
        s=str(f.readline(),encoding="utf-8",errors="replace")
        if s.startswith("#-") or not s:break
        print(s,end="")

if __name__=="__main__":
    main()
    input()
