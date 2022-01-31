# Listing_1-2.py
# Copyright Warren & Csrter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Number Guessing program from Chapter 1

import random
secret = random.randint(1, 99)     # Pick a secret number
guess = 0
tries = 0
print "AHOY!  I'm the Dread Pirate Roberts, and I have a secret!"
print "It is a number from 1 to 99.  I'll give you 6 tries. "

# Allow up to 6 guesses
while guess != secret and tries < 6:                
    guess = input("What's yer guess? ")   # Get the player's guess
    if guess < secret:
        print "Too low, ye scurvy dog!"
    elif guess > secret:
        print "Too high, landlubber!"

    tries = tries + 1            # Use up one try               

# Print message at end of game
if guess == secret:                           \
    print "Avast! Ye got it!  Found my secret, ye did!"
else:
    print "No more guesses!  Better luck next time, matey!"
    print "The secret number was", secret
