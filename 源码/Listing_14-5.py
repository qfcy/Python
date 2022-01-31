# Listing_14-5.py
# Copyright Warren & Carter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# The start of our Hot Dog program

class HotDog:
    def __init__(self):
        self.cooked_level = 0
        self.cooked_string = "Raw"
        self.condiments = []
    
    def cook(self, time):
        # increase cooked_level by the amount of time
        self.cooked_level = self.cooked_level + time
        # set the strings for the different cooked levels
        if self.cooked_level > 8:                     
            self.cooked_string = "Charcoal"             
        elif self.cooked_level > 5:                     
            self.cooked_string = "Well-done"            
        elif self.cooked_level > 3:                     
            self.cooked_string = "Medium"               
        else:                                           
            self.cooked_string = "Raw"                  

myDog = HotDog()                         # create an instance

print myDog.cooked_level
print myDog.cooked_string
print myDog.condiments
