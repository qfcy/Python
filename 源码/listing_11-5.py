# Listing_11-5.py
# Copyright Warren & Carter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Printing the loop variables with nested loops

numBlocks = int(raw_input('How many blocks of stars do you want? '))
for block in range(1, numBlocks + 1):
    print 'block = ', block                         #Displays variables
    for line in range(1, block * 2 ):
        for star in range(1, (block + line) * 2): 
            print '*',
        print '  line = ', line, 'star = ', star    #Displays variables
    print

