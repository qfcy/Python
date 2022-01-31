# TIO_CH22_3.py
# Copyright Warren & Carter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Answer to Try It Out, Question 3, Chapter 22

# Save some data to a pickle file

import pickle

name = raw_input("Enter your name: ")
age = raw_input("Enter your age: ")
color = raw_input("Enter your favorite color: ")
food = raw_input("Enter your favorite food: ")

my_list = [name, age, color, food]

pickle_file = open("my_pickle_file.pkl", 'w')
pickle.dump(my_list, pickle_file)

pickle_file.close()
