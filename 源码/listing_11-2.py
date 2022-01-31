# Listing_11-2.py
# Copyright Warren & Carter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# A variable nested loop

numLines = int(raw_input ('How many lines of stars do you want? '))
numStars = int(raw_input ('How many stars per line? '))
for line in range(0, numLines):
    for star in range(0, numStars): 
        print '*',
    print
