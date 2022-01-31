# TIO_CH19_1.py
# Copyright Warren & Carter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Answer to Try It Out Question 1 in Chapter 19

# Number Guess game with sound

import random, pygame, sys
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode([200,100])  #make a small pygame window

ahoy = pygame.mixer.Sound("Ahoy.wav")
tooLow = pygame.mixer.Sound("TooLow.wav")
tooHigh = pygame.mixer.Sound("TooHigh.wav")
whatGuess = pygame.mixer.Sound("WhatsYerGuess.wav")
gotIt = pygame.mixer.Sound("AvastGotIt.wav")
noMore = pygame.mixer.Sound("NoMore.wav")

ahoy.set_volume(0.4)
tooLow.set_volume(0.4)
tooHigh.set_volume(0.4)
whatGuess.set_volume(0.4)
gotIt.set_volume(0.4)
noMore.set_volume(0.4)

secret = random.randint(1, 100)     # pick a secret number
guess = 0
tries = 0

print "AHOY!  I'm the Dread Pirate Roberts, and I have a secret!"
print "It is a number from 1 to 99.  I'll give you 6 tries. "
ahoy.play()
pygame.time.delay(8000)  # wait for the sound to finish playing

# try until they guess it or run out of turns

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running - False

    while guess != secret and tries < 6:
        whatGuess.play()
        guess = input("What's yer guess? ")       # get the player's guess
        if guess < secret:
            print "Too low, ye scurvy dog!"
            tooLow.play()
            pygame.time.delay(2200)   # wait for the sound to finish playing
        elif guess > secret:
            print "Too high, landlubber!"
            tooHigh.play()
            pygame.time.delay(1800)   # wait for the sound to finish playing
        tries = tries + 1                         # used up one try

    # print message at end of game    
    if guess == secret:
        print "Avast! Ye got it!  Found my secret, ye did!"
        gotIt.play()
        pygame.time.delay(3200)   # wait for the sound to finish playing
        running = False
    else:
        print "No more guesses!  Better luck next time, matey!"
        noMore.play()
        pygame.time.delay(3700)   # wait for the sound to finish playing
        running = False
pygame.quit()
