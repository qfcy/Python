import curses,random
#Import module msgbox to show error messages
try:
    import msgbox
    msgbox.init()
except (ImportError,AttributeError):pass

FOOD='$'
SNAKE='@'

def show_score(win,score):
    win.addstr(1,69,b"Score: %d"%score)

def main(stdscr):
    # initialize the window
    curses.curs_set(0)
    hei, wei = stdscr.getmaxyx()  # the value of first getting is y,not x
    w = curses.newwin(hei, wei, 0, 0)
    w.keypad(1)
    w.timeout(100)
    # initialize the color
    curses.start_color()
    curses.init_pair(9,curses.COLOR_WHITE,curses.COLOR_YELLOW)
    curses.init_pair(1,curses.COLOR_WHITE,curses.COLOR_GREEN)
    # initialize the position of snake
    sn_x = int(wei/4)
    sn_y = int(hei/2)
    snake = [[sn_y, sn_x], [sn_y, sn_x-1], [sn_y, sn_x-2]]

    # initialize the position of food
    food_pos = [int(hei/2), int(wei/2)]
    w.addch(food_pos[0], food_pos[1], FOOD,curses.color_pair(1))
     
    key = curses.KEY_RIGHT
    show_score(w,len(snake))

    # start
    while True:
        next_key = w.getch()  # The program stops waiting for user input. If not input for 100 milliseconds,go on
        if next_key != -1:  # got the input char
            if key == curses.KEY_RIGHT and next_key != curses.KEY_LEFT \
                    or key == curses.KEY_LEFT and next_key != curses.KEY_RIGHT \
                    or key == curses.KEY_DOWN and next_key != curses.KEY_UP \
                    or key == curses.KEY_UP and next_key != curses.KEY_DOWN:
                    key = next_key
                
        # the situation of death
        if snake[0][0] in [0, hei] or snake[0][1] in [0, wei] or snake[0] in snake[1:]:
            return
     
        # update the 'snake'
        temp = snake[0][0]
        temp2 = snake[0][1]
        new_head = [temp, temp2]
        if key == curses.KEY_RIGHT:
            new_head[1] += 1
        if key == curses.KEY_LEFT:
            new_head[1] -= 1
        if key == curses.KEY_DOWN:
            new_head[0] += 1
        if key == curses.KEY_UP:
            new_head[0] -= 1
        snake.insert(0, new_head)
     
        # the situation of eating food
        if snake[0] == food_pos:
            show_score(w,len(snake))
            food_pos = None
            while food_pos is None:
                new_food = [random.randint(1, hei-1), random.randint(1, wei-1)]
                if new_food not in snake:
                    food_pos = new_food
            w.addch(food_pos[0], food_pos[1], FOOD,curses.color_pair(1))
        else:
            tail = snake.pop()
            w.addch(tail[0], tail[1], ' ')  # remove the tail
     
        # snake move
        try:
            w.addch(snake[0][0], snake[0][1], SNAKE,curses.color_pair(9))
        except curses.error:return

if __name__=="__main__":curses.wrapper(main)
