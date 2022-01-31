# Listing_22-6.py
# Copyright Warren & Csrter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Using pickle to store a list to a file

import pickle
my_list  = ['Fred', 73, 'Hello there', 81.9876e-13]
pickle_file = open('my_pickled_list.pkl', 'w')
pickle.dump(my_list, pickle_file)
pickle_file.close()
