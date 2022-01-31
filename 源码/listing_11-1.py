# Listing_11-1.py
# Copyright Warren & Carter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Printing three multiplication tables at once

for multiplier in range (5, 8):                                    #B
    for i in range (1, 11):                                 #A     #B
        print i, "x", multiplier, "=", i * multiplier       #A     #B
    print                                                          #B

#A This inner loop prints a single table
#B This outer loop runs 3 iterations, with values 5, 6, 7
