# Listing_22-3.py
# Copyright Warren & Csrter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# using append mode

todo_list = open('notes.txt', 'a')     # Opens the file in append mode
todo_list.write('\nSpend allowance')   # Adds our string to the end
todo_list.close()                      # Closes the file

