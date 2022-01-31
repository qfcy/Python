import turtle,time
from turtle import *
def switchpen():
    if isdown():
        pu()
    else:
        pd()

def demo1():
        """Demo of old turtle.py - module"""
        reset()
        tracer(True)
        up()
        backward(100)
        down()
        # draw 3 squares; the last filled
        width(3)
        for i in range(3):
            if i == 2:
                begin_fill()
            for _ in range(4):
                forward(20)
                left(90)
            if i == 2:
                color("maroon")
                end_fill()
            up()
            forward(30)
            down()
        width(1)
        color("black")
        # move out of the way
        tracer(False)
        up()
        right(90)
        forward(100)
        right(90)
        forward(100)
        right(180)
        down()
        # some text
        write("startstart", 1)
        write("start", 1)
        color("red")
        # staircase
        for i in range(5):
            forward(20)
            left(90)
            forward(20)
            right(90)
        # filled staircase
        tracer(True)
        begin_fill()
        for i in range(5):
            forward(20)
            left(90)
            forward(20)
            right(90)
        end_fill()
        # more text

def demo2():
    """Demo of some new features."""
    speed(1)
    st()
    pensize(3)
    setheading(towards(0, 0))
    radius = distance(0, 0)/2.0
    rt(90)
    for _ in range(18):
        switchpen()
        circle(radius, 10)
    write("wait a moment...")
    while undobufferentries():
        undo()
    reset()
    lt(90)
    colormode(255)
    laenge = 10
    pencolor("green")
    pensize(3)
    lt(180)
    for i in range(-2, 16):
        if i > 0:
            begin_fill()
            fillcolor(255-15*i, 0, 15*i)
        for _ in range(3):
            fd(laenge)
            lt(120)
        end_fill()
        laenge += 10
        lt(15)
        speed((speed()+1)%12)
        #end_fill()

    lt(120)
    pu()
    fd(70)
    rt(30)
    pd()
    color("red","yellow")
    speed(0)
    begin_fill()
    for _ in range(4):
        circle(50, 90)
        rt(90)
        fd(30)
        rt(90)
    end_fill()
    lt(90)
    pu()
    fd(30)
    pd()
    shape("turtle")
    
    tri = getturtle()
    tri.resizemode("auto")
    turtle = Turtle()
    turtle.resizemode("auto")
    turtle.shape("turtle")
    turtle.reset()
    turtle.left(90)
    turtle.speed(0)
    turtle.up()
    turtle.goto(280, 40)
    turtle.lt(30)
    turtle.down()
    turtle.speed(6)
    turtle.color("blue","orange")
    turtle.pensize(2)
    tri.speed(6)
    setheading(towards(turtle))
    count = 1
    while tri.distance(turtle) > 4:
        turtle.fd(3.5)
        turtle.lt(0.6)
        tri.setheading(tri.towards(turtle))
        tri.fd(4)
        if count % 20 == 0:
            turtle.stamp()
            tri.stamp()
            switchpen()
        count += 1
    tri.write("CAUGHT! ", font=("Arial", 16, "bold"), align="right")
    tri.pencolor("black")
    tri.pencolor("red")
    
    def baba(xdummy, ydummy):
        clearscreen()
        bye()

    time.sleep(2)

    while undobufferentries():
        tri.undo()
        turtle.undo()
    tri.fd(50)
    tri.write("  Click me!", font = ("Courier", 12, "bold") )
    tri.onclick(baba, 1)

if __name__=="__main__":
    try:
        demo1()
        demo2()
        exitonclick()
    except Terminator:pass
