# TIO_CH12_4.py
# Copyright Warren & Carter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Answer to Try It Out Question 4 in Chapter 12

nameList = []
print "Enter 5 names (press the Enter key after each name):"
for i in range(5):
    name = raw_input()
    nameList.append(name)

print "The names are:", nameList
print "Replace one name.  Which one? (1-5):",
replace = int(raw_input())
new = raw_input("New name: ")
nameList[replace - 1] = new
print "The names are:", nameList


