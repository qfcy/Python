# Listing_23-1.py
# Copyright Warren & Csrter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Rolling a single 11-sided die 1,000 times

import random

totals = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]   # List has 13 items, with index 0 to 12 
for i in range(1000):
    dice_total = random.randint(2, 12)
    totals[dice_total] += 1                        # Adds 1 to the count of this total 
    
for i in range (2, 13):
    print "total", i, "came up", totals[i], "times"

