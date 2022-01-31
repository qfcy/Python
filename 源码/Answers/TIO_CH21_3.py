# TIO_CH21_3.py
# Copyright Warren & Carter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Answer to Try It Out, Question 3, Chapter 21

# Calculate all the fractions of 8 and display them
#   with 3 decimal places

for i in range(1, 9):
    fraction = i / 8.0
    print str(i) + '/8 = %.3f' % fraction
    
