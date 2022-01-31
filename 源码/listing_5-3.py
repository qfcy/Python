# Listing_5-3.py
# Copyright Warren & Carter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Temperature conversion program

print "This program converts Fahrenheit to Celsius"
print "Type in a temperature in Fahrenheit: ",
fahrenheit = float(raw_input())           # Get the Fahrenheit temperature from the user
celsius = (fahrenheit - 32) * 5.0 / 9
print "That is",                          # Notice the commas at the ends
print celsius,                            #   of these lines
print "degrees Celsius"
