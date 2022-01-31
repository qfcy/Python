# Listing_22-2.py
# Copyright Warren & Csrter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Using readline() more than once

my_file = open('notes.txt', 'r')
first_line = my_file.readline()
second_line = my_file.readline()
print "first line = ", first_line
print "second line = ", second_line
my_file.close()
