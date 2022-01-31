# Listing_11-6.py
# Copyright Warren & Carter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# program to figure out combinations of hot dog ingredients

print "\tDog \tBun \tKetchup\tMustard\tOnions"
count = 1
for dog in [0, 1]:                                 # dog loop
    for bun in [0, 1]:                             # bun loop
        for ketchup in [0, 1]:                     # ketchup loop
            for mustard in [0, 1]:                 # mustard loop
                for onion in [0, 1]:               # onion loop
                    print "#", count, "\t",
                    print dog, "\t", bun, "\t", ketchup, "\t",
                    print mustard, "\t", onion
                    count = count + 1
        
