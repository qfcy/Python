# Listing_23-6.py
# Copyright Warren & Csrter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Main loop of Crazy Eights

# Note that this is not a complete program.  It needs to be put together
#   with the other parts of Crazy Eights to make a working program.

init_cards()
while not game_done:
    blocked = 0
    player_turn()                                                   
    if len(p_hand) == 0:     # player has no cards left, so he wins                                         
        game_done = True                                            
        print                                                       
        print "You won!"                                            
    if not game_done:                                               
        computer_turn()                                             
    if len(c_hand) == 0:     # computer has no cards left, so it wins                                       
        game_done = True                                            
        print                                                       
        print "Computer won!"                                       
    if blocked >= 2:         # both players are blocked, so game ends                                   
        game_done = True
        print "Both players blocked.  GAME OVER."
