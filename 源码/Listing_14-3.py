# Listing_14-3.py
# Copyright Warren & Carter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Adding an __init__() method

class Ball:
    def __init__(self, color, size, direction):    # Here is the 
        self.color = color                         # __init__() method 
        self.size = size                           # 
        self.direction = direction                 #

    def bounce(self):
        if self.direction == "down":
            self.direction = "up"

myBall = Ball("red", "small", "down")              # Create an instance
                                                   # with some attributes
print "I just created a ball."
print "My ball is", myBall.size
print "My ball is", myBall.color
print "My ball's direction is ", myBall.direction
print "Now I'm going to bounce the ball"
print
myBall.bounce()
print "Now the ball's direction is", myBall.direction
