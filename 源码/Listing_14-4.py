# Listing_14-4.py
# Copyright Warren & Carter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Using __str__() to change how the object prints

class Ball:
    def __init__(self, color, size, direction):    
        self.color = color                         
        self.size = size                           
        self.direction = direction

   # here's the special method __str__()   
    def __str__(self):                                               
        msg = "Hi, I'm a " + self.size + " " + self.color + " ball!"   
        return msg                                                    

myBall = Ball("red", "small", "down")              
print myBall
