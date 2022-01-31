# Listing_22-7.py
# Copyright Warren & Csrter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Unpickling using load()

import pickle
pickle_file = open('my_pickled_list.pkl', 'r')
recovered_list = pickle.load(pickle_file)
pickle_file.close()

print recovered_list
