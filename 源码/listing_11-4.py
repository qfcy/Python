# Listing_11-4.py
# Copyright Warren & Carter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# A trickier variable nested loop

numBlocks = int(raw_input('How many blocks of stars do you want? '))
for block in range(1, numBlocks + 1):
    for line in range(1, block * 2 ):                # Formulas for number of lines 
        for star in range(1, (block + line) * 2):    #   and stars
            print '*',
        print
    print

