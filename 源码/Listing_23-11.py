# Listing_23-11.py
# Copyright Warren & Csrter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Crazy Eights - the main loop with scoring added

# Note that this is not a complete program.  It needs to be put together
#   with the other parts of Crazy Eights to make a working program.

done = False
p_total = c_total = 0
while not done:    
    game_done = False
    blocked = 0
    init_cards()        # set up deck and create player's and computer's hands                                                    
    while not game_done:
        player_turn() 
        if len(p_hand) == 0:     # player won                                         
            game_done = True
            print
            print "You won!"
            # display game score here
            p_points = 0
            for card in c_hand:                                           
                p_points += card.value     # add up points from computer's remaining cards                     
            p_total += p_points            # add points from this game to the total                               
            print"You got %i points for computer's hand" % p_points
        if not game_done: 
            computer_turn()
        if len(c_hand) == 0:        # computer won                                      
            game_done = True
            print
            print "Computer won!"
            # display game score here
            c_points = 0
            for card in p_hand:                                           
                c_points += card.value      # add up points from player's remaining cards                             
            c_total += c_points             # add points from this game to the total                              
            print"Computer got %i points for your hand" % c_points
        if blocked >= 2:                    # both player and computer blocked, so both get points
            game_done = True                                              
            print "Both players blocked.  GAME OVER."                     
            player_points = 0                                             
            for card in c_hand:                                           
                p_points += card.value                                    
            p_total += p_points                                           
            c_points = 0                                                  
            for card in p_hand:                                           
                c_points += card.value                                    
            c_total += c_points
            # print points for this game
            print"You got %i points for computer's hand" % p_points       
            print"Computer got %i points for your hand" % c_points        
    play_again = raw_input("Play again (Y/N)? ")
    if play_again.lower().startswith('y'):
        done = False
        # print total points so far
        print "\nSo far, you have %i points" % p_total                    
        print  "and the computer has %i points.\n" % c_total                   
    else:
        done = True
        
# print final totals            
print "\n Final Score:"                                                   
print "You: %i     Computer: %i" % (p_total, c_total)                     
