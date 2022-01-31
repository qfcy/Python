# Listing_8-9.py
# Copyright Warren & Carter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Using continue in a loop

for i in range (1, 6):
    print
    print 'i =', i,
    print 'Hello, how',
    if i == 3:
        continue
    print 'are you today?'
