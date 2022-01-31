# Listing_23-9.py
# Copyright Warren & Csrter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Crazy Eights - getting the new suit when the player plays an 8

# Note that this is not a complete program.  It needs to be put together
#   with the other parts of Crazy Eights to make a working program.

def get_new_suit():
    global active_suit
    got_suit = False
    while not got_suit:        # keep trying until the player enters a valid suit                                      
        suit = raw_input("Pick a suit: ")
        if suit.lower() == 'd':
            active_suit = "Diamonds"
            got_suit = True
        elif suit.lower() == 's':
            active_suit = "Spades"
            got_suit = True
        elif suit.lower() == 'h':
            active_suit = "Hearts"
            got_suit = True
        elif suit.lower() == 'c':
            active_suit = "Clubs"
            got_suit = True
        else:
            print"Not a valid suit.  Try again. ",  
    print "You picked", active_suit
