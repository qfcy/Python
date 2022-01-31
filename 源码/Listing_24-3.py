# Listing_24-3.py
# Copyright Warren & Csrter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Saving time to a pickle file

import datetime, pickle                                                    
import os                                                                  

first_time = True
if os.path.isfile("last_run.pkl"):            # check if pickle file exists                               
    pickle_file = open("last_run.pkl", 'r')   # open the pickle file for reading                             
    last_time = pickle.load(pickle_file)      # unpickle the datetime object                             
    pickle_file.close()
    print "The last time this program was run was ", last_time
    first_time = False
    
pickle_file = open("last_run.pkl", 'w')     # open (or create) the pickle file for writing                               
pickle.dump(datetime.datetime.now(), pickle_file)   # pickle the datetime object of the current time                     
pickle_file.close()
if first_time:
    print "Created new pickle file."
