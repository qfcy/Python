import math,turtle
def ellipse(a,b,angle,steps):
    minAngle = (2*math.pi/360) * angle / steps
    turtle.penup()
    turtle.setpos(0,-b)
    turtle.pendown()
    for i in range(steps):
        nextPoint = [a*math.sin((i+1)*minAngle),-b*math.cos((i+1)*minAngle)]
        turtle.setpos(nextPoint)

if __name__=="__main__":
    ellipse(200,100,360,30)
    turtle.done()