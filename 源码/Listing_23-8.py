# Listing_23-8.py
# Copyright Warren & Csrter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Crazy Eights - Getting the player's choice

# Note that this is not a complete program.  It needs to be put together
#   with the other parts of Crazy Eights to make a working program.

print("What would you like to do? ",end='')
response = input("Type a card to play or 'Draw' to take a card: " )
valid_play=False

# keep trying untile the player enters something valid
while not valid_play:                                                     
    selected_card = None               # get a card the player holds, or "draw"
    while selected_card == None:                                          
        if response.lower() == 'draw':
            # if choice is "draw" get a card from the deck and add it
            #   to the player's hand
            valid_play = True
            if len(deck) > 0:   
                card = random.choice(deck)                                
                p_hand.append(card)                                       
                deck.remove(card)                                         
                print("You drew", card.short_name)
            else:                                                         
                print("There are no cards left in the deck")
                blocked += 1                                              
        else:
            for card in p_hand:       # check if the selected card is in the player's hand
                if response.upper() == card.short_name:                   
                    selected_card = card
            if selected_card == None:
                response = input("You don't have that card. Try again:")

    if selected_card.rank == '8':     # playing an 8 is always legal                                  
        valid_play = True
        is_eight = True
    elif selected_card.suit  == active_suit:                              
        valid_play = True
    elif selected_card.rank  == up_card.rank:                             
        valid_play = True
                                
    if not valid_play:
        response = input("That's not a legal play.  Try again: ")
