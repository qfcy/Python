# Listing_13-4
# Copyright Warren & Carter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Creating and using a function that returns a value

# Function to calculate tax and return the total
def calculateTax(price, tax_rate):                       
    total = price + (price * tax_rate)                   
    return total                      # send the total back to the caller              

my_price = float(raw_input ("Enter a price: "))          

# Call the function and store the result in totalPrice
totalPrice = calculateTax(my_price, 0.06) 
               
print "price = ", my_price, " Total price = ", totalPrice
