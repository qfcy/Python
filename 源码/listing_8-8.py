# Listing_8-8.py
# Copyright Warren & Carter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# A while loop

print "Type 3 to continue, anything else to quit."
someInput = raw_input()

# Keep looping as long as someInput ='3'
while someInput == '3':
    print "Thank you for the 3.  Very kind of you."
    print "Type 3 to continue, anything else to quit."    # Body of the loop
    someInput = raw_input()                               #
print "That's not 3, so I'm quitting now."


