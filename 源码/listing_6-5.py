# Listing_6-5.py
# Copyright Warren & Carter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Number Guess game using EasyGui

import random, easygui
secret = random.randint(1, 99)         # Picks a secret number
guess = 0
tries = 0
easygui.msgbox("""AHOY!  I'm the Dread Pirate Roberts, and I have a secret!
It is a number from 1 to 99.  I'll give you 6 tries.""")

# Allows up to 6 guesses
while guess != secret and tries < 6:
    guess = easygui.integerbox("What's yer guess, matey?")      # Gets the player's guess
    if not guess: break
    if guess < secret:
        easygui.msgbox(str(guess) + " is too low, ye scurvy dog!")
    elif guess > secret:
        easygui.msgbox(str(guess) + " is too high, landlubber!")
    tries = tries + 1       # Uses up one try

# Prints message at end of game
if guess == secret:
    easygui.msgbox("Avast! Ye got it!  Found my secret, ye did!")
else:
    easygui.msgbox("No more guesses!  The number was " + str(secret))


