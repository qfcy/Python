# Listing_23-10.py
# Copyright Warren & Csrter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Crazy Eights - the computer's turn

# Note that this is not a complete program.  It needs to be put together
#   with the other parts of Crazy Eights to make a working program.

def computer_turn():
    global c_hand, deck, up_card, active_suit, blocked
    options = []
    for card in c_hand:
        if card.rank == '8':           # computer plays an 8                                     
            c_hand.remove(card)
            up_card  = card
            print "  Computer played ", card.short_name
            #suit totals:  [diamonds, hearts, spades, clubs]     
            suit_totals = [0, 0, 0, 0]     # count how many cards of each suit are held                             
            for suit in range(1, 5): 
                for card in c_hand:
                    if card.suit_id == suit:
                        suit_totals[suit-1] += 1
            long_suit = 0                  # the suit with the most cards is the "long suit"
            for i in range (4):
                if suit_totals[i] > long_suit:
                    long_suit = i
            
            # make the long suit the active suit
            if long_suit == 0:                                            
                active_suit = "Diamonds"                                  
            if long_suit == 1:                                            
                active_suit = "Hearts"                                    
            if long_suit == 2:                                            
                active_suit = "Spades"                                    
            if long_suit == 3:                                            
                active_suit = "Clubs"                                     
            print "  Computer changed suit to ", active_suit
            return         # done computer's hand - back to main loop                                               
        else:                                                     
            if card.suit == active_suit:       # see what cards are possible plays                           
                options.append(card)                                      
            elif card.rank == up_card.rank:                               
                options.append(card)                                      
                    
    if len(options) > 0:
        best_play = options[0]                # see which play option is best (highest value)
        for card in options:                                              
            if card.value > best_play.value:                              
                best_play = card                                          
        c_hand.remove(best_play)              # play computer's card                                 
        up_card = best_play                                               
        active_suit = up_card.suit                                        
        print "  Computer played ", best_play.short_name                  
            
    else:                                # no possible plays, so draw 
        if len(deck) >0:                 # (if there are any cards in the deck)
            next_card = random.choice(deck)                               
            c_hand.append(next_card)                                      
            deck.remove(next_card)                                        
            print "  Computer drew a card"                                  
        else:                            # no cards left in deck, so computer is blocked
            print"  Computer is blocked"                                  
            blocked += 1                                                  
    print "Computer has %i cards left" % (len(c_hand))
