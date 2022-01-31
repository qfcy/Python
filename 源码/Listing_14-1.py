# Listing_14-1.py
# Copyright Warren & Carter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# create a simple Ball class
class Ball:      # This tells Python we're making a class                       
                
    def bounce(self):                   # This is a method
        if self.direction == "down":    #
            self.direction = "up"       #
