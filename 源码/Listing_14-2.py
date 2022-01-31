# Listing_14-2.py
# Copyright Warren & Carter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# using the Ball class

class Ball:                                 # Here is our class        
                                            # definition
    def bounce(self):                       #     
        if self.direction == "down":        #       
            self.direction = "up"           #        

myBall = Ball()                             # Create an instance
myBall.direction = "down"                   # Set some attributes        
myBall.color = "red"                        #         
myBall.size = "small"                       #        

print "I just created a ball."                       
print "My ball is", myBall.size             # Display object attributes         
print "My ball is", myBall.color                     
print "My ball's direction is", myBall.direction     
print "Now I'm going to bounce the ball"
print
myBall.bounce()                             # bounce the ball
print "Now the ball's direction is", myBall.direction
