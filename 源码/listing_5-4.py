# Listing_5-4.py
# Copyright Warren & Carter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Getting input from the web

import urllib2
file = urllib2.urlopen('http://helloworldbook.com/data/message.txt')
message = file.read() 
print message
