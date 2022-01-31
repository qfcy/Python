# Listing_22-1.py
# Copyright Warren & Csrter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Opening and reading from a file

my_file = open('notes.txt', 'r')
lines = my_file.readlines()
print lines
