# Listing_8-6.py
# Copyright Warren & Carter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Ready for lift off!  (counting backwards)

import time
for i in range (10, 0, -1):         #Counts backward
    print i
    time.sleep(1)                   #Waits one second
print "BLAST OFF!"
