# Listing_13-6.py
# Copyright Warren & Carter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Using a global variable inside a function

# Define function calculateTax
def calculateTax(price, tax_rate):
    total = price + (price * tax_rate)
    print my_price                        # try to print my_price
    return total                                            

# Main program calls the function  
my_price = float(raw_input ("Enter a price: "))

totalPrice = calculateTax(my_price, 0.06)                   
print "price = ", my_price, " Total price = ", totalPrice
