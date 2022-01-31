# Listing_23-5.py
# Copyright Warren & Csrter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Making a deck of cards

# Note that this is not a complete program.  It needs to be put together
#   with the other parts of Crazy Eights to make a working program.

import random
from cards import Card    # import the Cards module

# use nested for loops to make a deck of cards
deck = []                                           
for suit_id in range(1, 5):                           
    for rank_id in range(1, 14):    
        deck.append(Card(suit_id, rank_id))        

# draw 5 cards from the deck to make a hand
hand = []                                           
for cards in range(0, 5):                          
    a = random.choice(deck)                         
    hand.append(a)                                  
    deck.remove(a)                                  

print    
for card in hand:
    print card.short_name, '=' ,card.long_name, "  Value:", card.value
