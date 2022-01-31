# Listing_13-7.py
# Copyright Warren & Carter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Trying to modify a global variable inside a function 

#Define function calculateTax
def calculateTax(price, tax_rate):                       
    total = price + (price * tax_rate)                   
    my_price = 10000                                 # Modify my_price inside the function    
    print "my_price (inside function) = ", my_price  # Print the local version of my_price    
    return total                                         

# Main program calls the function 
my_price = float(raw_input ("Enter a price: "))          

totalPrice = calculateTax(my_price, 0.06)                
print "price = ", my_price, " Total price = ", totalPrice
print "my_price (outside function) = ",my_price     # Print the global version of my_price     
