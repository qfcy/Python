# Listing_15-2.py
# Copyright Warren & Carter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Using a module

# my_module contains the c_to_f() function
import my_module

celsius = float(raw_input ("Enter a temperature in Celsius: "))
fahrenheit = c_to_f(Celsius)
print "That's ", fahrenheit, " degrees Fahrenheit"

# This  code will give an error message.
# The error is expected as explained in chapter 15.
