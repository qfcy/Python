# Listing_23-3.py
# Copyright Warren & Csrter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Looking for 10 heads in a row

from random import *
coin = ["Heads", "Tails"]
heads_in_row = 0
ten_heads_in_row = 0
for i in range (1000000):
    if choice(coin) == "Heads":    # Flip the coin
        heads_in_row += 1
    else:
        heads_in_row = 0

    if heads_in_row == 10:
        ten_heads_in_row += 1      #Got 10 heads in a row, increment counter
        heads_in_row = 0
   
print "We got 10 heads in a row", ten_heads_in_row, "times."

