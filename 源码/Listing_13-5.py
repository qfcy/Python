# Listing_13-5.py
# Copyright Warren & Carter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Trying to print a local variable

# Function to calculate tax and return the total
def calculateTax(price, tax_rate):
    total = price + (price * tax_rate)
    return total                                            
 
my_price = float(raw_input ("Enter a price: "))

# Call the function and store and print the result
totalPrice = calculateTax(my_price, 0.06)                   
print "price = ", my_price, " Total price = ", totalPrice

print price     #this line will cause an error
